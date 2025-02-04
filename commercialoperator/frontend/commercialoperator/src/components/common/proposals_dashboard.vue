<template id="proposal_dashboard">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="row mb-1">
                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="">Status</label>
                            <select
                                v-model="filterProposalStatus"
                                class="form-control"
                            >
                                <option value="All">All</option>
                                <option
                                    v-for="s in proposal_status"
                                    :key="s.value"
                                    :value="s.value"
                                >
                                    {{ s.name }}
                                </option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="">Submitter</label>
                            <select
                                v-model="filterProposalSubmitter"
                                class="form-control"
                            >
                                <option value="All">All</option>
                                <option
                                    v-for="s in proposal_submitters"
                                    :key="s.email"
                                    :value="s.email"
                                >
                                    {{ s.search_term }}
                                </option>
                            </select>
                        </div>
                    </div>
                    <div v-if="is_external" class="col-md-6">
                        <router-link
                            style="margin-top: 25px"
                            class="btn btn-primary pull-right"
                            :to="{ name: 'apply_proposal' }"
                            >New Application</router-link
                        >
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-3 mb-3">
                        <label for="">Lodged From</label>
                        <div
                            ref="proposalDateFromPicker"
                            class="input-group date"
                        >
                            <input
                                v-model="filterProposalLodgedFrom"
                                type="date"
                                class="form-control"
                                placeholder="DD/MM/YYYY"
                            />
                            <span class="input-group-addon">
                                <span
                                    class="glyphicon glyphicon-calendar"
                                ></span>
                            </span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <label for="">Lodged To</label>
                        <div
                            ref="proposalDateToPicker"
                            class="input-group date"
                        >
                            <input
                                v-model="filterProposalLodgedTo"
                                type="date"
                                class="form-control"
                                placeholder="DD/MM/YYYY"
                            />
                            <span class="input-group-addon">
                                <span
                                    class="glyphicon glyphicon-calendar"
                                ></span>
                            </span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="">Licence Type</label>
                            <select
                                v-model="filterApplicationType"
                                class="form-control"
                            >
                                <option value="All">All</option>
                                <option
                                    v-for="s in application_types"
                                    :key="s"
                                    :value="s"
                                >
                                    {{ s }}
                                </option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-12">
                        <datatable
                            v-if="level == 'external'"
                            :id="datatable_id"
                            ref="proposal_datatable"
                            :dt-options="proposal_ex_options"
                            :dt-headers="proposal_ex_headers"
                        />
                        <datatable
                            v-else
                            :id="datatable_id"
                            ref="proposal_datatable"
                            :dt-options="proposal_options"
                            :dt-headers="proposal_headers"
                        />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue';
import Vue from 'vue';

import { api_endpoints, helpers } from '@/utils/hooks';
export default {
    name: 'ProposalTableDash',
    components: {
        datatable,
    },
    props: {
        level: {
            type: String,
            required: true,
            validator: function (val) {
                let options = ['internal', 'referral', 'external'];
                return options.indexOf(val) != -1 ? true : false;
            },
        },
        url: {
            type: String,
            required: true,
        },
    },
    data() {
        let vm = this;
        return {
            pBody: 'pBody' + vm._uid,
            datatable_id: 'proposal-datatable-' + vm._uid,
            //Profile to check if user has access to process Proposal
            profile: {},
            is_payment_admin: false,
            // Filters for Proposals
            filterApplicationType: 'All',
            filterProposalStatus: 'All',
            filterProposalLodgedFrom: '',
            filterProposalLodgedTo: '',
            filterProposalSubmitter: 'All',
            dateFormat: 'DD/MM/YYYY',
            datepickerOptions: {
                format: 'DD/MM/YYYY',
                showClear: true,
                useCurrent: false,
                keepInvalid: true,
                allowInputToggle: true,
            },
            application_types: [],
            external_status: [
                { value: 'draft', name: 'Draft' },
                { value: 'with_assessor', name: 'Under Review' },
                { value: 'approved', name: 'Approved' },
                { value: 'declined', name: 'Declined' },
                { value: 'discarded', name: 'Discarded' },
                { value: 'awaiting_payment', name: 'Awaiting Payment' },
            ],
            internal_status: [
                { value: 'draft', name: 'Draft' },
                { value: 'with_assessor', name: 'With Assessor' },
                { value: 'on_hold', name: 'On Hold' },
                { value: 'with_qa_officer', name: 'With QA Officer' },
                { value: 'with_referral', name: 'With Referral' },
                {
                    value: 'with_assessor_requirements',
                    name: 'With Assessor (Requirements)',
                },
                { value: 'with_approver', name: 'With Approver' },
                { value: 'approved', name: 'Approved' },
                { value: 'declined', name: 'Declined' },
                { value: 'discarded', name: 'Discarded' },
                { value: 'awaiting_payment', name: 'Awaiting Payment' },
            ],
            proposal_submitters: [],
            proposal_status: [],
            proposal_ex_headers: [
                'Number',
                'Licence Type',
                'Submitter',
                'Applicant',
                'Status',
                'Lodged on',
                'Event Name',
                'Action',
            ],
            proposal_ex_options: {
                autoWidth: false,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>",
                },
                responsive: true,
                serverSide: true,
                order: [[0, 'desc']],
                lengthMenu: [
                    [10, 25, 50, 100, -1],
                    [10, 25, 50, 100, 'All'],
                ],
                ajax: {
                    url: vm.url,
                    dataSrc: 'data',

                    // adding extra GET params for Custom filtering
                    data: function (d) {
                        d.date_from =
                            vm.filterProposalLodgedFrom != '' &&
                            vm.filterProposalLodgedFrom != null
                                ? moment(vm.filterProposalLodgedFrom).format(
                                      'YYYY-MM-DD'
                                  )
                                : '';
                        d.date_to =
                            vm.filterProposalLodgedTo != '' &&
                            vm.filterProposalLodgedTo != null
                                ? moment(vm.filterProposalLodgedTo).format(
                                      'YYYY-MM-DD'
                                  )
                                : '';
                    },
                },
                dom: '<"container-fluid"<"row"<"col"l><"col"f><"col"<"float-end"B>>>>rtip', // 'lfBrtip'
                buttons: ['excel', 'csv'],
                columns: [
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            return full.lodgement_number;
                        },
                        name: 'id, lodgement_number',
                    },
                    {
                        data: 'application_type',
                        name: 'application_type__name',
                    },
                    {
                        data: 'submitter',
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            if (data && data.full_name) {
                                return `${data.full_name}`;
                            }
                            return '';
                        },
                        name: 'submitter__email',
                        searchable: false, // Note: disabled for now during segregation
                    },
                    {
                        data: 'applicant',
                        name: 'org_applicant__organisation__name, proxy_applicant__email, proxy_applicant__first_name, proxy_applicant__last_name',
                        searchable: false, // Note: disabled for now during segregation
                    },
                    {
                        data: 'customer_status',
                        //mRender:function(data,type,full){
                        //    return vm.level == 'internal' ? full.processing_status: data; //Fix the issue with External dashboard Status dropdown shoing internal statuses.
                        //},
                        name: 'customer_status',
                    },
                    {
                        data: 'lodgement_date',
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            return data != '' && data != null
                                ? moment(data).format(vm.dateFormat)
                                : '';
                        },
                        searchable: false, // handles by filter_queryset override method - class ProposalFilterBackend
                    },
                    {
                        data: 'event_name',
                        searchable: false,
                        orderable: false,
                        name: '',
                    },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            let links = '';
                            if (!vm.is_external) {
                                if (full.assessor_process) {
                                    links += `<a href='/internal/proposal/${full.id}'>Process</a><br/>`;
                                } else {
                                    links += `<a href='/internal/proposal/${full.id}'>View</a><br/>`;
                                }
                            } else {
                                if (full.can_user_edit) {
                                    links += `<a href='/external/proposal/${full.id}'>Continue</a><br/>`;
                                    links += `<a href='#${full.id}' data-discard-proposal='${full.id}'>Discard</a><br/>`;
                                } else if (full.can_user_view) {
                                    links += `<a href='/external/proposal/${full.id}'>View</a><br/>`;
                                }
                                if (
                                    full.customer_status ==
                                        'Awaiting Payment' &&
                                    !full.fee_paid
                                ) {
                                    links += `<a href='/filming_fee/${full.id}'>Make Payment</a><br/>`;
                                    links += `<a href='/cols/payments/awaiting-payment-pdf/${full.id}' target='_blank'><i style='color:red;' class='fa fa-file-pdf'>&nbsp</i>Pending Invoice</a><br/>`;
                                }
                            }
                            if (
                                full.fee_invoice_reference &&
                                full.proposal_type != 'Amendment'
                            ) {
                                if (full.application_type == 'Filming') {
                                    links += `<a href='/cols/payments/invoice-filmingfee-pdf/${full.fee_invoice_reference}' target='_blank'><i style='color:red;' class='fa fa-file-pdf'>&nbsp</i>#${full.fee_invoice_reference}</a><br/>`;
                                } else {
                                    links += `<a href='/cols/payments/invoice-pdf/${full.fee_invoice_reference}' target='_blank'><i style='color:red;' class='fa fa-file-pdf'>&nbsp</i>#${full.fee_invoice_reference}</a><br/>`;
                                }
                            }
                            return links;
                        },
                        name: '',
                        searchable: false,
                        orderable: false,
                    },
                ],
                processing: true,
            },
            proposal_headers: [
                'Number',
                'Licence Type',
                'Submitter',
                'Applicant',
                'Status',
                'Lodged on',
                'Assigned Officer',
                'Event Name',
                'Action',
            ],
            proposal_options: {
                autoWidth: false,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>",
                },
                responsive: true,
                serverSide: true,
                order: [[0, 'desc']],
                lengthMenu: [
                    [10, 25, 50, 100, -1],
                    [10, 25, 50, 100, 'All'],
                ],
                ajax: {
                    url: vm.url,
                    dataSrc: 'data',

                    // adding extra GET params for Custom filtering
                    data: function (d) {
                        d.date_from =
                            vm.filterProposalLodgedFrom != '' &&
                            vm.filterProposalLodgedFrom != null
                                ? moment(vm.filterProposalLodgedFrom).format(
                                      'YYYY-MM-DD'
                                  )
                                : '';
                        d.date_to =
                            vm.filterProposalLodgedTo != '' &&
                            vm.filterProposalLodgedTo != null
                                ? moment(vm.filterProposalLodgedTo).format(
                                      'YYYY-MM-DD'
                                  )
                                : '';
                    },
                },
                dom: '<"container-fluid"<"row"<"col"l><"col"f><"col"<"float-end"B>>>>rtip', // 'lfBrtip'
                buttons: ['excel', 'csv'],
                columns: [
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            return full.lodgement_number;
                        },
                    },
                    {
                        data: 'application_type',
                        name: 'application_type__name',
                    },
                    {
                        data: 'submitter',
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            if (data && data.full_name) {
                                return `${data.full_name}`;
                            }
                            return '';
                        },
                        name: 'submitter__email',
                        searchable: false, // Note: disabled for now during segregation
                    },
                    {
                        data: 'applicant',
                        name: 'applicant',
                        searchable: false, // Note: disabled for now during segregation
                    },
                    {
                        data: 'processing_status',
                        name: 'processing_status',
                    },
                    {
                        data: 'lodgement_date',
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            return data != '' && data != null
                                ? moment(data).format(vm.dateFormat)
                                : '';
                        },
                        searchable: false, // handles by filter_queryset override method - class ProposalFilterBackend
                    },
                    {
                        data: 'assigned_officer',
                        name: 'assigned_officer__first_name, assigned_officer__last_name',
                        searchable: false, // Note: disabled for now during segregation
                    },
                    {
                        data: 'event_name',
                        searchable: false,
                        orderable: false,
                        name: '',
                    },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            let links = '';
                            if (!vm.is_external) {
                                /*if(vm.check_assessor(full) && full.can_officer_process)*/
                                if (full.assessor_process) {
                                    links += `<a href='/internal/proposal/${full.id}'>Process</a><br/>`;
                                } else {
                                    links += `<a href='/internal/proposal/${full.id}'>View</a><br/>`;
                                }
                            } else {
                                if (full.can_user_edit) {
                                    links += `<a href='/external/proposal/${full.id}'>Continue</a><br/>`;
                                    links += `<a href='#${full.id}' data-discard-proposal='${full.id}'>Discard</a><br/>`;
                                } else if (full.can_user_view) {
                                    links += `<a href='/external/proposal/${full.id}'>View</a><br/>`;
                                }
                            }

                            if (
                                !full.fee_paid &&
                                full.processing_status == 'Awaiting Payment'
                            ) {
                                if (vm.is_payment_admin) {
                                    //links +=  `<a href='/ledger/payments/invoice/payment?invoice=${full.fee_invoice_reference}' target='_blank'>Record Payment</a><br/>`;
                                    links += `<a href='/filming_fee/${full.id}'>Record Payment</a><br/>`;
                                }
                                links += `<a href='/cols/payments/awaiting-payment-pdf/${full.id}' target='_blank'><i style='color:red;' class='fa fa-file-pdf'>&nbsp</i>Pending Invoice</a><br/>`;
                            }

                            //if (full.fee_paid && full.proposal_type!='Amendment'){
                            if (
                                full.fee_invoice_reference &&
                                full.proposal_type != 'Amendment'
                            ) {
                                if (vm.is_payment_admin) {
                                    links += `<a href='/ledger/payments/invoice/payment?invoice=${full.fee_invoice_reference}' target='_blank'>View Payment</a><br/>`;
                                }

                                if (full.application_type == 'Filming') {
                                    links += `<a href='/cols/payments/invoice-filmingfee-pdf/${full.fee_invoice_reference}' target='_blank'><i style='color:red;' class='fa fa-file-pdf'>&nbsp</i>#${full.fee_invoice_reference}</a><br/>`;
                                } else {
                                    links += `<a href='/cols/payments/invoice-pdf/${full.fee_invoice_reference}' target='_blank'><i style='color:red;' class='fa fa-file-pdf'>&nbsp</i>#${full.fee_invoice_reference}</a><br/>`;
                                }
                            }

                            return links;
                        },
                        name: '',
                        searchable: false,
                        orderable: false,
                    },
                ],
                processing: true,
            },
        };
    },
    computed: {
        is_external: function () {
            return this.level == 'external';
        },
        is_referral: function () {
            return this.level == 'referral';
        },
    },
    watch: {
        filterProposalSubmitter: function () {
            //this.$refs.proposal_datatable.vmDataTable.draw();
            let vm = this;
            if (vm.filterProposalSubmitter != 'All') {
                vm.$refs.proposal_datatable.vmDataTable
                    .columns(2)
                    .search(vm.filterProposalSubmitter)
                    .draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable
                    .columns(2)
                    .search('')
                    .draw();
            }
        },
        filterProposalStatus: function () {
            let vm = this;
            if (vm.filterProposalStatus != 'All') {
                vm.$refs.proposal_datatable.vmDataTable
                    .columns(4)
                    .search(vm.filterProposalStatus)
                    .draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable
                    .columns(4)
                    .search('')
                    .draw();
            }
        },
        filterApplicationType: function () {
            let vm = this;
            if (vm.filterApplicationType != 'All') {
                vm.$refs.proposal_datatable.vmDataTable
                    .columns(1)
                    .search(vm.filterApplicationType)
                    .draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable
                    .columns(1)
                    .search('')
                    .draw();
            }
        },
        filterProposalLodgedFrom: function () {
            this.$refs.proposal_datatable.vmDataTable.ajax.reload(
                helpers.enablePopovers,
                false
            );
        },
        filterProposalLodgedTo: function () {
            this.$refs.proposal_datatable.vmDataTable.ajax.reload(
                helpers.enablePopovers,
                false
            );
        },
    },

    mounted: function () {
        this.fetchFilterLists();
        this.fetchProfile();
        let vm = this;
        $('a[data-toggle="collapse"]').on('click', function () {
            var chev = $(this).children()[0];
            window.setTimeout(function () {
                $(chev).toggleClass(
                    'glyphicon-chevron-down glyphicon-chevron-up'
                );
            }, 100);
        });
        this.$nextTick(() => {
            vm.initialiseSearch();
            vm.addEventListeners();
        });
    },
    methods: {
        make_payment: function (fee_invoice_reference) {
            const vm = this;
            vm.$http
                .post('/existing_invoice_payment/' + fee_invoice_reference)
                .then(
                    (response) => {
                        vm.res = response.body;
                    },
                    (error) => {
                        console.log(error);
                    }
                );
        },
        make_payment2: function (fee_invoice_reference) {
            let vm = this;
            var form = document.forms.new_payment;
            if (vm.payment_method == 'existing_invoice') {
                form.action =
                    '/existing_invoice_payment/' +
                    fee_invoice_reference +
                    '/?method=' +
                    vm.payment_method;
                form.submit();
            }
        },

        fetchFilterLists: function () {
            let vm = this;
            vm.$http.get(api_endpoints.filter_list).then(
                (response) => {
                    vm.proposal_submitters = response.body.submitters;
                    vm.application_types = response.body.application_types;
                    vm.proposal_status =
                        vm.level == 'internal'
                            ? vm.internal_status
                            : vm.external_status;
                },
                (error) => {
                    console.log(error);
                }
            );
        },

        discardProposal: function (proposal_id) {
            let vm = this;
            swal({
                title: 'Discard Application',
                text: 'Are you sure you want to discard this proposal?',
                type: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Discard Application',
                confirmButtonColor: '#d9534f',
            }).then(
                () => {
                    vm.$http
                        .delete(api_endpoints.discard_proposal(proposal_id))
                        .then(
                            () => {
                                swal(
                                    'Discarded',
                                    'Your proposal has been discarded',
                                    'success'
                                );
                                vm.$refs.proposal_datatable.vmDataTable.ajax.reload();
                            },
                            (error) => {
                                console.log(error);
                            }
                        );
                },
                () => {}
            );
        },
        addEventListeners: function () {
            let vm = this;
            // End Proposal Date Filters
            // External Discard listener
            vm.$refs.proposal_datatable.vmDataTable.on(
                'click',
                'a[data-discard-proposal]',
                function (e) {
                    e.preventDefault();
                    var id = $(this).attr('data-discard-proposal');
                    vm.discardProposal(id);
                }
            );
        },
        initialiseSearch: function () {
            this.submitterSearch();
            this.dateSearch();
        },
        submitterSearch: function () {
            let vm = this;
            vm.$refs.proposal_datatable.table.dataTableExt.afnFiltering.push(
                function (settings, data, dataIndex, original) {
                    let filtered_submitter = vm.filterProposalSubmitter;
                    if (filtered_submitter == 'All') {
                        return true;
                    }
                    return filtered_submitter == original.submitter.email;
                }
            );
        },
        dateSearch: function () {
            let vm = this;
            vm.$refs.proposal_datatable.table.dataTableExt.afnFiltering.push(
                function (settings, data, dataIndex, original) {
                    let from = vm.filterProposalLodgedFrom;
                    let to = vm.filterProposalLodgedTo;
                    let val = original.lodgement_date;

                    if (from == '' && to == '') {
                        return true;
                    } else if (from != '' && to != '') {
                        return val != null && val != ''
                            ? moment()
                                  .range(
                                      moment(from, vm.dateFormat),
                                      moment(to, vm.dateFormat)
                                  )
                                  .contains(moment(val))
                            : false;
                    } else if (from == '' && to != '') {
                        if (val != null && val != '') {
                            return moment(to, vm.dateFormat).diff(
                                moment(val)
                            ) >= 0
                                ? true
                                : false;
                        } else {
                            return false;
                        }
                    } else if (to == '' && from != '') {
                        if (val != null && val != '') {
                            return moment(val).diff(
                                moment(from, vm.dateFormat)
                            ) >= 0
                                ? true
                                : false;
                        } else {
                            return false;
                        }
                    } else {
                        return false;
                    }
                }
            );
        },

        fetchProfile: function () {
            let vm = this;
            Vue.http.get(api_endpoints.profile).then(
                (response) => {
                    vm.profile = response.body;
                    vm.is_payment_admin = response.body.is_payment_admin;
                },
                (error) => {
                    console.log(error);
                }
            );
        },

        check_assessor: function (proposal) {
            let vm = this;
            if (proposal.assigned_officer) {
                {
                    if (proposal.assigned_officer == vm.profile.full_name)
                        return true;
                    else return false;
                }
            } else {
                var assessor = proposal.allowed_assessors.filter(
                    function (elem) {
                        return (elem.id = vm.profile.id);
                    }
                );

                if (assessor.length > 0) return true;
                else return false;
            }
        },
    },
};
</script>
<style scoped>
.dt-buttons {
    float: right;
}
</style>
