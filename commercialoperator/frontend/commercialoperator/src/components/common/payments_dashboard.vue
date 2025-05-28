<template id="proposal_dashboard">
    <div id="paymentDash" class="container">
        <div
            v-if="is_external && overdue_invoices.length > 0"
            class="row error"
        >
            <div class="col-sm-12 mb-2">
                <div class="card">
                    <div class="card-header">
                        The following invoice(s) are overdue:
                    </div>
                    <div class="well well-sm card-body">
                        <div class="card-text">
                            <div
                                v-for="invoice in overdue_invoices"
                                :key="invoice.id"
                            >
                                {{ invoice.invoice_reference }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-sm-12">
                <div v-if="is_external" class="card mb-2">
                    <div class="card-header">Park Entry Fees</div>
                    <div class="card-body">
                        <p class="card-text">
                            Entry fees apply to passenger
                            <a :href="payment_help_url" target="_blank"
                                ><i
                                    class="fa fa-question-circle"
                                    style="color: blue"
                                    >&nbsp;</i
                                ></a
                            >
                        </p>
                    </div>
                </div>
                <FormSection
                    :form-collapse="false"
                    label="Park Entry Fees"
                    index="park_entry_fees"
                    subtitle=""
                >
                    <div class="row">
                        <div class="col-md-3">
                            <div
                                id="select_park_entry_fees_parks_parent"
                                class="form-group"
                            >
                                <label for="select_park_entry_fees_parks"
                                    >Park</label
                                >
                                <select
                                    id="select_park_entry_fees_parks"
                                    ref="select_park_entry_fees_parks"
                                    v-model="filterProposalPark"
                                    class="form-control"
                                >
                                    <option value="All">All</option>
                                    <option
                                        v-for="p in proposal_parks"
                                        :key="p.id"
                                        :value="p.id"
                                    >
                                        {{ p.name }}
                                    </option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div
                                id="select_park_entry_fees_status_parent"
                                class="form-group"
                            >
                                <label for="select_park_entry_fees_status"
                                    >Status</label
                                >
                                <select
                                    id="select_park_entry_fees_status"
                                    ref="select_park_entry_fees_status"
                                    v-model="filterProposalStatus"
                                    class="form-control"
                                >
                                    <option value="All">All</option>
                                    <option
                                        v-for="s in payment_status"
                                        :key="s.value"
                                        :value="s.value"
                                    >
                                        {{ s.name }}
                                    </option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div
                                id="select_park_entry_fees_payment_method_parent"
                                class="form-group"
                            >
                                <label
                                    for="select_park_entry_fees_payment_method"
                                    >Payment Method</label
                                >
                                <select
                                    id="select_park_entry_fees_payment_method"
                                    ref="select_park_entry_fees_payment_method"
                                    v-model="filterProposalPaymentMethod"
                                    class="form-control"
                                >
                                    <option value="All">All</option>
                                    <option
                                        v-for="s in payment_method"
                                        :key="s.value"
                                        :value="s.value"
                                    >
                                        {{ s.name }}
                                    </option>
                                </select>
                            </div>
                        </div>
                        <div v-if="is_external" class="col-md-3">
                            <div class="form-group">
                                <router-link
                                    style="margin-top: 25px"
                                    class="btn btn-primary pull-right"
                                    :to="{ name: 'external-payment_order' }"
                                    >Make Payment</router-link
                                >
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="input_proposal_lodged_from"
                                    >Arrival From</label
                                >
                                <div
                                    ref="proposalDateFromPicker"
                                    class="input-group date"
                                >
                                    <input
                                        id="input_proposal_lodged_from"
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
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="input_proposal_lodged_to"
                                    >Arrival To</label
                                >
                                <div
                                    ref="proposalDateToPicker"
                                    class="input-group date"
                                >
                                    <input
                                        id="input_proposal_lodged_to"
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
                </FormSection>
            </div>
        </div>
    </div>
</template>
<script>
import FormSection from '@/components/forms/section_toggle.vue';
import datatable from '@/utils/vue/datatable.vue';
import Vue from 'vue';

import { api_endpoints, helpers } from '@/utils/hooks';
export default {
    name: 'ProposalTableDash',
    components: {
        FormSection,
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
    },
    data() {
        let vm = this;
        return {
            pBody: 'pBody' + vm._uid,
            datatable_id: 'proposal-datatable-' + vm._uid,
            //Profile to check if user has access to process Proposal
            profile: {},
            is_payment_admin: false,
            overdue_invoices: [],
            // Filters for Proposals
            filterProposalPark: 'All',
            filterProposalStatus: 'All',
            filterProposalPaymentMethod: 'All',
            filterProposalLodgedFrom: '',
            filterProposalLodgedTo: '',
            filterProposalSubmitter: 'All',
            dateFormat: 'DD/MM/YYYY',
            payment_status: [
                { name: 'Paid', value: 'paid' },
                { name: 'Over Paid', value: 'over_paid' },
                { name: 'Partially Paid', value: 'partially_paid' },
                { name: 'Unpaid', value: 'unpaid' },
                { name: 'Overdue', value: 'overdue' },
            ],
            payment_method: [
                { name: 'Credit Card', value: '0' },
                { name: 'BPAY', value: '1' },
                { name: 'Monthly Invoicing', value: '2' },
                { name: 'Other', value: '3' },
            ],
            proposal_submitters: [],
            proposal_parks: [],
            proposal_headers: [
                ' Number',
                'Licence',
                'Holder',
                'Trading name',
                'Status',
                'Payment Method',
                'Arrival',
                'Park',
                'Visitors',
                'Invoice/Confirmation',
                'Action',
            ],
            proposal_options: {
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>",
                },
                responsive: true,
                serverSide: true,
                lengthMenu: [
                    [10, 25, 50, 100, -1],
                    [10, 25, 50, 100, 'All'],
                ],
                ajax: {
                    //"url": vm.url,
                    //"url": '/api/booking_paginated/bookings_external/?format=datatables',
                    url: api_endpoints.booking_paginated_internal,
                    dataSrc: 'data',

                    // adding extra GET params for Custom filtering
                    data: function (d) {
                        d.park =
                            vm.filterProposalPark != 'All' &&
                            vm.filterProposalPark != null
                                ? vm.filterProposalPark
                                : '';
                        d.payment_status =
                            vm.filterProposalStatus != 'All' &&
                            vm.filterProposalStatus != null
                                ? vm.filterProposalStatus
                                : '';
                        d.payment_method =
                            vm.filterProposalPaymentMethod != 'All' &&
                            vm.filterProposalPaymentMethod != null
                                ? vm.filterProposalPaymentMethod
                                : '';
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
                        data: 'admission_number',
                        name: 'admission_number',
                    },
                    {
                        data: 'approval_number',
                        name: 'proposal__approval__lodgement_number',
                    },
                    {
                        data: 'applicant',
                        name: 'proposal__approval__org_applicant__organisation__name, proposal__approval__proxy_applicant__email, proposal__approval__proxy_applicant__first_name, proposal__approval__proxy_applicant__last_name',
                        visible: this.level == 'internal' ? true : false,
                    },
                    {
                        data: 'trading_name',
                        name: 'proposal__org_applicant__organisation__trading_name, proposal__org_applicant__organisation__name',
                    },
                    {
                        data: 'payment_status',
                        name: 'payment_status',
                        searchable: false,
                        orderable: false,
                    },
                    {
                        data: 'payment_method',
                        name: 'payment_method',
                        searchable: false,
                        orderable: false,
                    },
                    {
                        data: 'park_bookings',
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            let arrival_dates = '';
                            _.forEach(data, function (park) {
                                arrival_dates +=
                                    (park.arrival != '' && park.arrival != null
                                        ? moment(park.arrival).format(
                                              vm.dateFormat
                                          )
                                        : '') + '<br>';
                                //arrival_dates += arrival_dates + '<br>'
                            });
                            return arrival_dates;
                        },
                        searchable: false,
                        orderable: true,
                    },
                    {
                        data: 'park_bookings',
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            let parks = '';
                            _.forEach(data, function (item) {
                                parks += item.park + '<br>';
                            });
                            return parks;
                        },
                        //name: "park__id, park__name"
                        name: 'park_bookings__park__name',
                    },
                    {
                        data: 'park_bookings',
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            let visitors = '';
                            _.forEach(data, function (item) {
                                visitors +=
                                    'A: ' +
                                    item.no_adults +
                                    '; C: ' +
                                    item.no_children +
                                    '; F: ' +
                                    item.no_free_of_charge +
                                    '<br>';
                            });
                            return visitors;
                        },
                        searchable: false,
                        orderable: true,
                    },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            let links = '';
                            if (
                                full.payment_status.toLowerCase() == 'paid' ||
                                full.payment_method.toUpperCase() == 'BPAY' ||
                                (full.payment_method.toLowerCase() ==
                                    'monthly invoicing' &&
                                    full.invoice_reference !== null)
                            ) {
                                links += `<a href='/cols/payments/invoice-pdf/${full.invoice_reference}.pdf' target='_blank'><i style='color:red;' class='fa fa-file-pdf'>&nbsp</i></a>`;
                                links += `<a href='/cols/payments/confirmation-pdf/${full.invoice_reference}.pdf' target='_blank'><i style='color:red;' class='fa fa-file-pdf'></i></a><br/>`;
                            } else if (
                                full.payment_method.toLowerCase() ==
                                    'monthly invoicing' &&
                                full.invoice_reference == null
                            ) {
                                // running aggregated monthly booking - not yet invoiced
                                links += `<a href='/cols/payments/monthly-confirmation-pdf/booking/${full.id}.pdf' target='_blank' style='padding-left: 52px;'><i style='color:red;' class='fa fa-file-pdf'></i></a><br/>`;
                            }
                            return links;
                        },
                        name: '',
                        searchable: false,
                        orderable: false,
                    },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            let links = '';
                            if (vm.is_payment_admin) {
                                if (
                                    full.payment_status.toLowerCase() ==
                                        'paid' ||
                                    full.payment_status.toLowerCase() ==
                                        'over_paid'
                                ) {
                                    links += `<a href='/cols/payments/invoice-payment-view/${full.invoice_reference}' target='_blank'>View Payment</a><br/>`;
                                } else if (full.invoice_reference !== null) {
                                    links += `<a href='/cols/payments/invoice-payment-view/${full.invoice_reference}' target='_blank'>Record Payment</a><br/>`;
                                }
                            }
                            return links;
                        },
                        name: '',
                        searchable: false,
                        orderable: false,
                        visible: vm.level == 'internal' ? true : false,
                    },
                ],
                processing: true,
            },
        };
    },
    computed: {
        status: function () {
            //return this.is_external ? this.external_status : this.internal_status;
            return [];
        },
        is_external: function () {
            return this.level == 'external';
        },
        is_internal: function () {
            return this.level == 'internal';
        },
        payment_help_url: function () {
            return api_endpoints.payment_help_url;
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
        filterProposalPaymentMethod: function () {
            let vm = this;
            if (vm.filterProposalPaymentMethod != 'All') {
                vm.$refs.proposal_datatable.vmDataTable
                    .columns(4)
                    .search(vm.filterProposalPaymentMethod)
                    .draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable
                    .columns(4)
                    .search('')
                    .draw();
            }
        },
        filterProposalPark: function () {
            let vm = this;
            vm.$refs.proposal_datatable.vmDataTable
                .columns(6)
                .search('')
                .draw();
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
        this.fetchOverdueInvoices();
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
            vm.addEventListeners();
            vm.initialiseSearch();
        });
    },
    methods: {
        fetchFilterLists: function () {
            let vm = this;

            vm.$http.get(api_endpoints.filter_list_approvals).then(
                (response) => {
                    vm.proposal_submitters = response.body.submitters;
                    //vm.approval_status = response.body.approval_status_choices;
                },
                (error) => {
                    console.log(error);
                }
            );

            vm.$http.get(api_endpoints.filter_list_parks).then(
                (response) => {
                    vm.proposal_parks = response.body;
                },
                (error) => {
                    console.log(error);
                }
            );

            //console.log(vm.regions);
        },
        fetchOverdueInvoices: function () {
            let vm = this;

            vm.$http.get(api_endpoints.overdue_invoices).then(
                (response) => {
                    vm.overdue_invoices = response.body;
                },
                (error) => {
                    console.log(error);
                }
            );
        },

        addEventListeners: function () {
            let vm = this;
            // Internal Reissue listener
            vm.$refs.proposal_datatable.vmDataTable.on(
                'click',
                'a[data-reissue-approval]',
                function (e) {
                    e.preventDefault();
                    var id = $(this).attr('data-reissue-approval');
                    vm.reissueApproval(id);
                }
            );

            // Internal Extend listener
            vm.$refs.proposal_datatable.vmDataTable.on(
                'click',
                'a[data-extend-approval]',
                function (e) {
                    e.preventDefault();
                    var id = $(this).attr('data-extend-approval');
                    vm.extendApproval(id);
                }
            );

            //Internal Cancel listener
            vm.$refs.proposal_datatable.vmDataTable.on(
                'click',
                'a[data-cancel-approval]',
                function (e) {
                    e.preventDefault();
                    var id = $(this).attr('data-cancel-approval');
                    vm.cancelApproval(id);
                }
            );

            //Internal Suspend listener
            vm.$refs.proposal_datatable.vmDataTable.on(
                'click',
                'a[data-suspend-approval]',
                function (e) {
                    e.preventDefault();
                    var id = $(this).attr('data-suspend-approval');
                    vm.suspendApproval(id);
                }
            );

            // Internal Reinstate listener
            vm.$refs.proposal_datatable.vmDataTable.on(
                'click',
                'a[data-reinstate-approval]',
                function (e) {
                    e.preventDefault();
                    var id = $(this).attr('data-reinstate-approval');
                    vm.reinstateApproval(id);
                }
            );

            //Internal/ External Surrender listener
            vm.$refs.proposal_datatable.vmDataTable.on(
                'click',
                'a[data-surrender-approval]',
                function (e) {
                    e.preventDefault();
                    var id = $(this).attr('data-surrender-approval');
                    vm.surrenderApproval(id);
                }
            );

            // External renewal listener
            vm.$refs.proposal_datatable.vmDataTable.on(
                'click',
                'a[data-renew-approval]',
                function (e) {
                    e.preventDefault();
                    var id = $(this).attr('data-renew-approval');
                    vm.renewApproval(id);
                }
            );

            // External amend listener
            vm.$refs.proposal_datatable.vmDataTable.on(
                'click',
                'a[data-amend-approval]',
                function (e) {
                    e.preventDefault();
                    var id = $(this).attr('data-amend-approval');
                    vm.amendApproval(id);
                }
            );

            helpers.initialiseSelect2.bind(this)(
                'select_park_entry_fees_parks',
                'select_park_entry_fees_parks_parent',
                'filterProposalPark',
                'Select Park',
                false
            );
            helpers.initialiseSelect2.bind(this)(
                'select_park_entry_fees_status',
                'select_park_entry_fees_status_parent',
                'filterProposalStatus',
                'Select Status',
                false
            );
            helpers.initialiseSelect2.bind(this)(
                'select_park_entry_fees_payment_method',
                'select_park_entry_fees_payment_method_parent',
                'filterProposalPaymentMethod',
                'Select Payment Method',
                false
            );
        },
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
                    let from = vm.filterProposalLodgedFrom;
                    let to = vm.filterProposalLodgedTo;
                    let val = original.expiry_date;

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

        refreshFromResponse: function () {
            this.$refs.proposal_datatable.vmDataTable.ajax.reload();
        },
    },
};
</script>
<style scoped>
.error {
    color: red;
}
</style>
