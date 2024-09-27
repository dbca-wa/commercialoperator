<template id="proposal_dashboard">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">
                        Licences
                        <small v-if="is_external"
                            >View existing licences and amend or renew
                            them</small
                        >
                        <a
                            :href="'#' + pBody"
                            data-toggle="collapse"
                            data-parent="#userInfo"
                            expanded="true"
                            :aria-controls="pBody"
                        >
                            <span
                                class="glyphicon glyphicon-chevron-up pull-right"
                            ></span>
                        </a>
                    </h3>
                </div>
                <div :id="pBody" class="panel-body collapse in">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Status</label>
                                <select
                                    v-model="filterProposalStatus"
                                    class="form-control"
                                >
                                    <option value="All">All</option>
                                    <option
                                        v-for="s in approval_status"
                                        :key="s"
                                        :value="s"
                                    >
                                        {{ s }}
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
                            <div class="form-group">
                                <label for="">Start From</label>
                                <div
                                    ref="startDateFromPicker"
                                    class="input-group date"
                                >
                                    <input
                                        v-model="filterStartFrom"
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
                                <label for="">Start To</label>
                                <div
                                    ref="startDateToPicker"
                                    class="input-group date"
                                >
                                    <input
                                        v-model="filterStartTo"
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
                                <label for="">Expiry From</label>
                                <div
                                    ref="expiryDateFromPicker"
                                    class="input-group date"
                                >
                                    <input
                                        v-model="filterExpiryFrom"
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
                                <label for="">Expiry To</label>
                                <div
                                    ref="expiryDateToPicker"
                                    class="input-group date"
                                >
                                    <input
                                        v-model="filterExpiryTo"
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

                        <div v-if="is_internal" class="col-md-3">
                            <div class="form-group">
                                <label />
                                <div>
                                    <button
                                        style="width: 80%"
                                        class="btn btn-primary top-buffer-s"
                                        :disabled="disabled"
                                        @click.prevent="createEClassLicence()"
                                    >
                                        New E Class licence
                                    </button>
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
                </div>
            </div>
        </div>
        <ApprovalExtend
            ref="approval_extend"
            @refreshFromResponse="refreshFromResponse"
        ></ApprovalExtend>
        <ApprovalCancellation
            ref="approval_cancellation"
            @refreshFromResponse="refreshFromResponse"
        ></ApprovalCancellation>
        <ApprovalSuspension
            ref="approval_suspension"
            @refreshFromResponse="refreshFromResponse"
        ></ApprovalSuspension>
        <ApprovalSurrender
            ref="approval_surrender"
            @refreshFromResponse="refreshFromResponse"
        ></ApprovalSurrender>
        <EClassLicence ref="eclass_licence"></EClassLicence>
    </div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue';
import Vue from 'vue';
import ApprovalExtend from '../internal/approvals/approval_extend.vue';
import ApprovalCancellation from '../internal/approvals/approval_cancellation.vue';
import ApprovalSuspension from '../internal/approvals/approval_suspension.vue';
import ApprovalSurrender from '../internal/approvals/approval_surrender.vue';
import EClassLicence from '../internal/approvals/approval_eclass.vue';

import { api_endpoints, helpers } from '@/utils/hooks';
export default {
    name: 'ProposalTableDash',
    components: {
        datatable,
        ApprovalExtend,
        ApprovalCancellation,
        ApprovalSuspension,
        ApprovalSurrender,
        EClassLicence,
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
        disabled: {
            type: Boolean,
            default: false,
        },
    },
    data() {
        let vm = this;
        return {
            pBody: 'pBody' + vm._uid,
            datatable_id: 'proposal-datatable-' + vm._uid,
            //Profile to check if user has access to process Proposal
            profile: {},
            // Filters for Proposals
            filterApplicationType: 'All',
            filterProposalStatus: 'All',
            filterStartFrom: '',
            filterStartTo: '',
            filterExpiryFrom: '',
            filterExpiryTo: '',
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
            approval_status: [],
            proposal_submitters: [],
            proposal_headers: [
                'Number',
                'Application',
                'Licence Type',
                'Holder',
                'Status',
                'Start Date',
                'Expiry Date',
                'Licence',
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
                        d.start_date_from =
                            vm.filterStartFrom != '' &&
                            vm.filterStartFrom != null
                                ? moment(vm.filterStartFrom).format(
                                      'YYYY-MM-DD'
                                  )
                                : '';
                        d.start_date_to =
                            vm.filterStartTo != '' && vm.filterStartTo != null
                                ? moment(vm.filterStartTo).format('YYYY-MM-DD')
                                : '';
                        d.expiry_date_from =
                            vm.filterExpiryFrom != '' &&
                            vm.filterExpiryFrom != null
                                ? moment(vm.filterExpiryFrom).format(
                                      'YYYY-MM-DD'
                                  )
                                : '';
                        d.expiry_date_to =
                            vm.filterExpiryTo != '' && vm.filterExpiryTo != null
                                ? moment(vm.filterExpiryTo).format('YYYY-MM-DD')
                                : '';
                    },
                },
                dom: 'lBfrtip',
                buttons: ['excel', 'csv'],
                columns: [
                    {
                        data: 'id',
                        render: function (data, type, full) {
                            if (!vm.is_external) {
                                var result = '';
                                var popTemplate = '';
                                var message = '';
                                let tick = '';
                                tick =
                                    "<i class='fa fa-exclamation-triangle' style='color:red'></i>";
                                result = full.reserved_licence
                                    ? '<span>' +
                                      full.lodgement_number +
                                      ' (R) </span>'
                                    : '<span>' +
                                      full.lodgement_number +
                                      '</span>';
                                if (full.can_reissue) {
                                    if (!full.can_action) {
                                        if (full.set_to_cancel) {
                                            message =
                                                'This Licence is marked for cancellation to future date';
                                        }
                                        if (full.set_to_suspend) {
                                            message =
                                                'This Licence is marked for suspension to future date';
                                        }
                                        if (full.set_to_surrender) {
                                            message =
                                                'This Licence is marked for surrendering to future date';
                                        }
                                        popTemplate = _.template(
                                            '<a href="#" ' +
                                                'role="button" ' +
                                                'data-toggle="popover" ' +
                                                'data-trigger="hover" ' +
                                                'data-placement="top auto"' +
                                                'data-html="true" ' +
                                                'data-content="<%= text %>" ' +
                                                '><%= tick %></a>'
                                        );
                                        result += popTemplate({
                                            text: message,
                                            tick: tick,
                                        });
                                    }
                                }
                                return result;
                            } else {
                                return full.lodgement_number;
                            }
                        },
                        createdCell: helpers.dtPopoverCellFn,
                        name: 'lodgement_number',
                    },
                    {
                        data: 'linked_applications',
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            let applications = '';
                            _.forEach(data, function (item) {
                                applications += item + '<br>';
                            });
                            return applications;
                        },
                        name: 'current_proposal__lodgement_number',
                    },

                    {
                        data: 'application_type',
                        name: 'current_proposal__application_type__name',
                    },
                    {
                        data: 'applicant',
                        name: 'org_applicant__organisation__name, proxy_applicant__email, proxy_applicant__first_name, proxy_applicant__last_name',
                        // Note: Set to non-searchable because for now we can't search in ledger fields (emailuser, organisation)
                        searchable: false,
                    },
                    { data: 'status' },
                    {
                        data: 'start_date',
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            return data != '' && data != null
                                ? moment(data).format(vm.dateFormat)
                                : '';
                        },
                        searchable: false,
                    },
                    {
                        data: 'expiry_date',
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            return data != '' && data != null
                                ? moment(data).format(vm.dateFormat)
                                : '';
                        },
                        searchable: false,
                    },
                    {
                        data: 'licence_document',
                        mRender: function (data, type, full) {
                            var result = '';
                            var popTemplate = '';
                            if (!full.migrated) {
                                result = `<a href="${data}" target="_blank"><i style="color:red" class="fa fa-file-pdf-o"></i></a>`;
                            } else if (full.migrated) {
                                var icon =
                                    "<i class='fa fa-file-pdf-o' style='color:red'></i>";
                                var message = 'This is a migrated licence';
                                popTemplate = _.template(
                                    '<a href="#" ' +
                                        'role="button" ' +
                                        'data-toggle="popover" ' +
                                        'data-trigger="hover" ' +
                                        'data-placement="top auto"' +
                                        'data-html="true" ' +
                                        'data-content="<%= text %>" ' +
                                        '><%= tick %></a>'
                                );
                                result += popTemplate({
                                    text: message,
                                    tick: icon,
                                });
                            }
                            if (full.requirement_docs) {
                                _.forEach(
                                    full.requirement_docs,
                                    function (item) {
                                        result += `<br><a href="${item[1]}" target="_blank">${item[0]}</a>`;
                                    }
                                );
                            }
                            return result;
                        },
                        createdCell: helpers.dtPopoverCellFn,
                        name: 'licence_document__name',
                    },
                    {
                        data: 'licence_name',
                        searchable: false,
                        orderable: false,
                        name: '',
                    },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            let links = '';
                            if (!vm.is_external) {
                                if (full.is_approver) {
                                    if (!full.is_lawful_authority) {
                                        if (full.can_reissue) {
                                            links += `<a href='#${full.id}' data-reissue-approval='${full.current_proposal}'>Reissue</a><br/>`;
                                        }
                                    }
                                }
                                if (full.is_assessor) {
                                    if (full.is_lawful_authority) {
                                        if (full.can_reissue_lawful_authority) {
                                            links += `<a href='#${full.id}' data-reissue-approval='${full.current_proposal}'>Reissue</a><br/>`;
                                        }
                                    }
                                    if (
                                        full.application_type == 'E Class' &&
                                        (full.status == 'Current' ||
                                            full.status == 'Suspended')
                                    ) {
                                        if (full.can_extend) {
                                            links += `<a href='#${full.id}' data-extend-approval='${full.id}'>Extend</a><br/>`;
                                        } else {
                                            links += `<a class='disabled' title='Licence has already been extended' style="color: grey;text-decoration: none;">Extend</a><br/>`;
                                        }
                                    }
                                    if (full.can_reissue && full.can_action) {
                                        if (full.is_lawful_authority) {
                                            if (
                                                full.can_reissue_lawful_authority
                                            ) {
                                                links += `<a href='#${full.id}' data-cancel-approval='${full.id}'>Cancel</a><br/>`;
                                                links += `<a href='#${full.id}' data-surrender-approval='${full.id}'>Surrender</a><br/>`;
                                            }
                                        } else {
                                            links += `<a href='#${full.id}' data-cancel-approval='${full.id}'>Cancel</a><br/>`;
                                            links += `<a href='#${full.id}' data-surrender-approval='${full.id}'>Surrender</a><br/>`;
                                        }
                                    }
                                    if (
                                        full.status == 'Current' &&
                                        full.can_action
                                    ) {
                                        if (full.is_lawful_authority) {
                                            if (
                                                full.is_lawful_authority_finalised
                                            ) {
                                                links += `<a href='#${full.id}' data-suspend-approval='${full.id}'>Suspend</a><br/>`;
                                            }
                                        } else {
                                            links += `<a href='#${full.id}' data-suspend-approval='${full.id}'>Suspend</a><br/>`;
                                        }
                                    }
                                    if (full.can_reinstate) {
                                        links += `<a href='#${full.id}' data-reinstate-approval='${full.id}'>Reinstate</a><br/>`;
                                    }
                                    links += `<a href='/internal/approval/${full.id}'>View</a><br/>`;
                                } else {
                                    links += `<a href='/internal/approval/${full.id}'>View</a><br/>`;
                                }
                                if (
                                    full.renewal_document &&
                                    full.renewal_sent
                                ) {
                                    links += `<a href='${full.renewal_document}' target='_blank'>Renewal Notice</a><br/>`;
                                }
                            } else {
                                //External Dashboard actions.
                                if (full.can_reissue) {
                                    links += `<a href='/external/approval/${full.id}'>View</a><br/>`;
                                    if (full.can_action) {
                                        if (full.is_lawful_authority) {
                                            if (
                                                full.can_reissue_lawful_authority
                                            ) {
                                                links += `<a href='#${full.id}' data-surrender-approval='${full.id}'>Surrender</a><br/>`;
                                            }
                                        } else {
                                            links += `<a href='#${full.id}' data-surrender-approval='${full.id}'>Surrender</a><br/>`;
                                        }

                                        if (full.can_amend) {
                                            links += `<a href='#${full.id}' data-amend-approval='${full.current_proposal}'>Amend</a><br/>`;
                                        }
                                    }
                                    if (
                                        full.renewal_document &&
                                        full.renewal_sent &&
                                        full.can_renew
                                    ) {
                                        links += `<a href='#${full.id}' data-renew-approval='${full.current_proposal}'>Renew</a><br/>`;
                                    }
                                } else {
                                    links += `<a href='/external/approval/${full.id}'>View</a><br/>`;
                                }
                            }
                            return links;
                        },
                        searchable: false,
                        orderable: false,
                        name: '',
                    },
                    { data: 'migrated', visible: false },
                ],
                processing: true,
            },
        };
    },
    computed: {
        status: function () {
            return [];
        },
        is_external: function () {
            return this.level == 'external';
        },
        is_internal: function () {
            return this.level == 'internal';
        },
        is_referral: function () {
            return this.level == 'referral';
        },
    },
    watch: {
        filterProposalSubmitter: function () {
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
        filterStartFrom: function () {
            this.$refs.proposal_datatable.vmDataTable.ajax.reload(
                helpers.enablePopovers,
                false
            );
        },
        filterStartTo: function () {
            this.$refs.proposal_datatable.vmDataTable.ajax.reload(
                helpers.enablePopovers,
                false
            );
        },
        filterExpiryFrom: function () {
            this.$refs.proposal_datatable.vmDataTable.ajax.reload(
                helpers.enablePopovers,
                false
            );
        },
        filterExpiryTo: function () {
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
        createEClassLicence: function () {
            this.$refs.eclass_licence.isModalOpen = true;
        },

        fetchFilterLists: function () {
            let vm = this;

            vm.$http.get(api_endpoints.filter_list_approvals).then(
                (response) => {
                    vm.proposal_submitters = response.body.submitters;
                    vm.approval_status = response.body.approval_status_choices;
                    vm.application_types = response.body.application_types;
                },
                (error) => {
                    console.log(error);
                }
            );
        },

        addEventListeners: function () {
            let vm = this;
            // End Proposal Date Filters
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
                    let from = vm.filterExpiryFrom;
                    let to = vm.filterExpiryTo;
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
                },
                (error) => {
                    console.log(error);
                }
            );
        },

        check_assessor: function (proposal) {
            let vm = this;

            var assessor = proposal.allowed_assessors.filter(function (elem) {
                return (elem.id = vm.profile.id);
            });
            if (assessor.length > 0) return true;
            else return false;
        },

        reissueApproval: function (proposal_id) {
            let vm = this;
            let status = 'with_approver';
            let data = { status: status };
            swal.fire({
                title: 'Reissue Licence',
                text: 'Are you sure you want to reissue this licence?',
                icon: 'warning',
                confirmButtonText: 'Reissue licence',
            }).then(
                () => {
                    vm.$http
                        .post(
                            helpers.add_endpoint_json(
                                api_endpoints.proposals,
                                proposal_id + '/reissue_approval'
                            ),
                            JSON.stringify(data),
                            {
                                emulateJSON: true,
                            }
                        )
                        .then(
                            () => {
                                vm.$router.push({
                                    name: 'internal-proposal',
                                    params: { proposal_id: proposal_id },
                                });
                            },
                            (error) => {
                                console.log(error);
                                swal.fire({
                                    title: 'Reissue Licence',
                                    text: error.body,
                                    icon: 'error',
                                });
                            }
                        );
                },
                () => {}
            );
        },

        _extendApproval: function (approval_id) {
            let vm = this;
            let status = 'with_approver';
            let data = { status: status };
            swal.fire({
                title: 'Renew Licence',
                text: "<input type='email' class='form-control' name='email' id='email'/>",
                icon: 'input',
                showCancelButton: true,
                confirmButtonText: 'Extend licence',
            }).then(
                () => {
                    vm.$http
                        .post(
                            helpers.add_endpoint_json(
                                api_endpoints.approvals,
                                approval_id + '/approval_extend'
                            ),
                            JSON.stringify(data),
                            {
                                emulateJSON: true,
                            }
                        )
                        .then(
                            () => {
                                vm.$router.push({
                                    name: 'internal-proposal',
                                    params: { approval_id: approval_id },
                                });
                            },
                            (error) => {
                                console.log(error);
                                swal.fire({
                                    title: 'Extend Licence',
                                    text: error.body,
                                    icon: 'error',
                                });
                            }
                        );
                },
                () => {}
            );
        },

        extendApproval: function (approval_id) {
            this.$refs.approval_extend.approval_id = approval_id;
            this.$refs.approval_extend.isModalOpen = true;
        },

        reinstateApproval: function (approval_id) {
            let vm = this;
            swal.fire({
                title: 'Reinstate Licence',
                text: 'Are you sure you want to reinstate this licence?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Reinstate licence',
            }).then(
                () => {
                    vm.$http
                        .post(
                            helpers.add_endpoint_json(
                                api_endpoints.approvals,
                                approval_id + '/approval_reinstate'
                            ),
                            {}
                        )
                        .then(
                            () => {
                                swal.fire({
                                    title: 'Reinstate',
                                    text: 'Your licence has been reinstated',
                                    icon: 'success',
                                });
                                vm.$refs.proposal_datatable.vmDataTable.ajax.reload();
                            },
                            (error) => {
                                console.log(error);
                                swal.fire({
                                    title: 'Reinstate Licence',
                                    text: error.body,
                                    icon: 'error',
                                });
                            }
                        );
                },
                () => {}
            );
        },

        renewApproval: function (proposal_id) {
            let vm = this;
            swal.fire({
                title: 'Renew Licence',
                text: 'Are you sure you want to renew this licence?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Renew licence',
            }).then(
                () => {
                    swal.fire({
                        title: 'Loading...',
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        onOpen: () => {
                            swal.showLoading();
                        },
                    });
                    vm.$http
                        .get(
                            helpers.add_endpoint_json(
                                api_endpoints.proposals,
                                proposal_id + '/renew_approval'
                            ),
                            {}
                        )
                        .then(
                            (response) => {
                                swal.hideLoading();
                                swal.close();
                                let proposal = {};
                                proposal = response.body;
                                vm.$router.push({
                                    name: 'draft_proposal',
                                    params: { proposal_id: proposal.id },
                                });
                            },
                            (error) => {
                                console.log(error);
                                swal.fire({
                                    title: 'Renew Licence',
                                    text: error.body,
                                    icon: 'error',
                                });
                            }
                        );
                },
                () => {}
            );
        },

        amendApproval: function (proposal_id) {
            let vm = this;
            swal.fire({
                title: 'Amend Licence',
                text: 'Are you sure you want to amend this licence?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Amend licence',
            }).then(
                () => {
                    swal.fire({
                        title: 'Loading...',
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        onOpen: () => {
                            swal.showLoading();
                        },
                    });
                    vm.$http
                        .get(
                            helpers.add_endpoint_json(
                                api_endpoints.proposals,
                                proposal_id + '/amend_approval'
                            ),
                            {}
                        )
                        .then(
                            (response) => {
                                swal.hideLoading();
                                swal.close();
                                let proposal = {};
                                proposal = response.body;
                                vm.$router.push({
                                    name: 'draft_proposal',
                                    params: { proposal_id: proposal.id },
                                });
                            },
                            (error) => {
                                console.log(error);
                                swal.fire({
                                    title: 'Amend Licence',
                                    text: error.body,
                                    icon: 'error',
                                });
                            }
                        );
                },
                () => {}
            );
        },

        cancelApproval: function (approval_id) {
            this.$refs.approval_cancellation.approval_id = approval_id;
            this.$refs.approval_cancellation.isModalOpen = true;
        },

        suspendApproval: function (approval_id) {
            this.$refs.approval_suspension.approval = {};
            this.$refs.approval_suspension.approval_id = approval_id;
            this.$refs.approval_suspension.isModalOpen = true;
        },

        surrenderApproval: function (approval_id) {
            this.$refs.approval_surrender.approval_id = approval_id;
            this.$refs.approval_surrender.isModalOpen = true;
        },

        refreshFromResponse: function () {
            this.$refs.proposal_datatable.vmDataTable.ajax.reload();
        },
    },
};
</script>
<style scoped></style>
