<template id="proposal_dashboard">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="row">
                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="">Status</label>
                            <select
                                v-model="filterComplianceStatus"
                                class="form-control"
                            >
                                <option value="All">All</option>
                                <option
                                    v-for="s in status"
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
                    <div class="col-md-3">
                        <label for="">Due date From</label>
                        <div
                            ref="complianceDateFromPicker"
                            class="input-group date"
                        >
                            <input
                                v-model="filterComplianceDueFrom"
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
                        <label for="">Due date To</label>
                        <div
                            ref="complianceDateToPicker"
                            class="input-group date"
                        >
                            <input
                                v-model="filterComplianceDueTo"
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
                </div>
                <div class="row">
                    <div class="col-lg-12" style="margin-top: 25px">
                        <datatable
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
            is_payment_admin: false,
            datatable_id: 'proposal-datatable-' + vm._uid,
            // Filters for Proposals
            filterApplicationType: 'All',
            filterProposalRegion: 'All',
            filterProposalActivity: 'All',
            filterComplianceStatus: 'All',
            filterComplianceDueFrom: '',
            filterComplianceDueTo: '',
            filterProposalSubmitter: 'All',
            dateFormat: 'DD/MM/YYYY',
            datepickerOptions: {
                format: 'DD/MM/YYYY',
                showClear: true,
                useCurrent: false,
                keepInvalid: true,
                allowInputToggle: true,
            },
            external_status: [
                { value: 'due', name: 'Due' },
                { value: 'future', name: 'Future' },
                { value: 'with_assessor', name: 'Under Review' },
                { value: 'approved', name: 'Approved' },
            ],
            internal_status: [
                { value: 'due', name: 'Due' },
                { value: 'future', name: 'Future' },
                { value: 'with_assessor', name: 'With Assessor' },
                { value: 'approved', name: 'Approved' },
            ],
            status: [],
            application_types: [],
            proposal_submitters: [],
            proposal_headers: [
                'Number',
                'Licence',
                'Licence Type',
                'Holder',
                'Status',
                'Due Date',
                'Assigned To',
                'Event Name',
                'Action',
            ],
            proposal_options: {
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
                            vm.filterComplianceDueFrom != '' &&
                            vm.filterComplianceDueFrom != null
                                ? moment(vm.filterComplianceDueFrom).format(
                                      'YYYY-MM-DD'
                                  )
                                : '';
                        d.date_to =
                            vm.filterComplianceDueTo != '' &&
                            vm.filterComplianceDueTo != null
                                ? moment(vm.filterComplianceDueTo).format(
                                      'YYYY-MM-DD'
                                  )
                                : '';
                    },
                },
                dom: 'lBfrtip',
                buttons: ['excel', 'csv'],
                columns: [
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            return full.reference;
                        },
                        name: 'id, lodgement_number',
                    },
                    {
                        data: 'approval_lodgement_number',
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            return data;
                        },
                        name: 'approval__lodgement_number',
                    },
                    {
                        data: 'application_type',
                        name: 'proposal__application_type__name',
                    },
                    {
                        data: 'holder',
                        name: 'approval__org_applicant__organisation__name, approval__proxy_applicant__email, approval__proxy_applicant__first_name, approval__proxy_applicant__last_name',
                    },
                    {
                        data: 'processing_status',
                        mRender: function (data, type, full) {
                            return vm.level == 'external'
                                ? full.customer_status
                                : data;
                        },
                    },
                    {
                        data: 'due_date',
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            return data != '' && data != null
                                ? moment(data).format(vm.dateFormat)
                                : '';
                        },
                    },
                    {
                        data: 'assigned_to',
                        name: 'assigned_to__first_name, assigned_to__last_name, assigned_to__email',
                    },
                    {
                        data: 'compliance_licence_name',
                        searchable: false,
                        orderable: false,
                        name: '',
                    },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            let links = '';
                            if (!vm.is_external) {
                                if (full.can_process) {
                                    links += `<a href='/internal/compliance/${full.id}'>Process</a><br/>`;
                                } else {
                                    links += `<a href='/internal/compliance/${full.id}'>View</a><br/>`;
                                }
                                if (full.fee_paid) {
                                    if (vm.is_payment_admin) {
                                        links += `<a href='/ledger/payments/invoice/payment?invoice=${full.fee_invoice_reference}' target='_blank'>View Payment</a><br/>`;
                                    }
                                }
                            } else {
                                if (full.can_user_view) {
                                    links += `<a href='/external/compliance/${full.id}'>View</a><br/>`;
                                } else {
                                    links += `<a href='/external/compliance/${full.id}'>Submit</a><br/>`;
                                }
                            }

                            if (full.fee_invoice_reference) {
                                links += `<a href='/cols/payments/invoice-compliance-pdf/${full.fee_invoice_reference}' target='_blank'><i style='color:red;' class='fa fa-file-pdf-o'></i>&nbsp #${full.fee_invoice_reference}</a><br/>`;
                            }

                            return links;
                        },
                        name: '',
                    },
                    { data: 'reference', visible: false },
                    { data: 'customer_status', visible: false },
                    { data: 'can_user_view', visible: false },
                    { data: 'can_process', visible: false },
                    { data: 'fee_invoice_reference', visible: false },
                    { data: 'fee_paid', visible: false },
                ],
                processing: true,
            },
        };
    },
    computed: {
        is_external: function () {
            return this.level == 'external';
        },
    },
    watch: {
        filterComplianceStatus: function () {
            let vm = this;
            if (vm.filterComplianceStatus != 'All') {
                vm.$refs.proposal_datatable.vmDataTable
                    .columns(4)
                    .search(vm.filterComplianceStatus)
                    .draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable
                    .columns(4)
                    .search('')
                    .draw();
            }
        },
        filterProposalSubmitter: function () {
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterComplianceDueFrom: function () {
            this.$refs.proposal_datatable.vmDataTable.ajax.reload(
                helpers.enablePopovers,
                false
            );
        },
        filterComplianceDueTo: function () {
            this.$refs.proposal_datatable.vmDataTable.ajax.reload(
                helpers.enablePopovers,
                false
            );
        },
        filterApplicationType: function () {
            let vm = this;
            if (vm.filterApplicationType != 'All') {
                vm.$refs.proposal_datatable.vmDataTable
                    .columns(2)
                    .search(vm.filterApplicationType)
                    .draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable
                    .columns(2)
                    .search('')
                    .draw();
            }
        },
    },
    mounted: function () {
        let vm = this;
        this.fetchProfile();
        vm.fetchFilterLists();
        $('a[data-toggle="collapse"]').on('click', function () {
            var chev = $(this).children()[0];
            window.setTimeout(function () {
                $(chev).toggleClass(
                    'glyphicon-chevron-down glyphicon-chevron-up'
                );
            }, 100);
        });
        this.$nextTick(() => {
            vm.addEventListeners();
            vm.initialiseSearch();
        });
        if (vm.is_external) {
            var column = vm.$refs.proposal_datatable.vmDataTable.columns(6); //Hide 'Assigned To column for external'
            column.visible(false);
        }
    },
    methods: {
        fetchFilterLists: function () {
            let vm = this;

            vm.status =
                vm.level == 'external'
                    ? vm.external_status
                    : vm.internal_status;

            vm.$http.get(api_endpoints.filter_list_compliances).then(
                (response) => {
                    vm.application_types = response.body.application_types;
                },
                (error) => {
                    console.log(error);
                }
            );
        },

        addEventListeners: function () {},
        initialiseSearch: function () {
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
                    let from = vm.filterComplianceDueFrom;
                    let to = vm.filterComplianceDueTo;
                    let val = original.due_date;

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
                () => {}
            );
        },
    },
};
</script>
<style scoped></style>
