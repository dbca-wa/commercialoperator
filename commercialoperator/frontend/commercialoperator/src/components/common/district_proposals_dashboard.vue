<template id="district_proposal_dashboard">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">
                        District Applications referred to me
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
                                        v-for="s in proposal_status"
                                        :key="s.value"
                                        :value="s.value"
                                    >
                                        {{ s.name }}
                                    </option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
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
                    </div>
                    <div class="row">
                        <div class="col-lg-12">
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
    </div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue';
import { api_endpoints, helpers } from '@/utils/hooks';
export default {
    name: 'DistrictProposalTableDash',
    components: {
        datatable,
    },
    props: {
        url: {
            type: String,
            required: true,
        },
    },

    data() {
        let vm = this;
        return {
            pBody: 'pBody' + vm._uid,
            datatable_id: 'district-proposal-datatable-' + vm._uid,
            // Filters for Proposals
            filterProposalRegion: [],
            filterProposalActivity: 'All',
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
            proposal_status: [],
            proposal_submitters: [],
            proposal_headers: [
                'Number',
                'Submitter',
                'Applicant',
                'Status',
                'Lodged on',
                'Action',
            ],
            proposal_options: {
                customProposalSearch: true,
                tableID: 'proposal-datatable-' + vm._uid,
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
                columns: [
                    {
                        data: 'proposal',
                        mRender: function (data, type, full) {
                            return full.proposal_lodgement_number;
                        },
                        name: 'proposal__id, proposal__lodgement_number',
                    },
                    {
                        data: 'submitter',
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            if (data) {
                                return `${data.first_name} ${data.last_name}`;
                            }
                            return '';
                        },
                        name: 'proposal__submitter__email',
                    },
                    {
                        data: 'applicant',
                        name: 'proposal__org_applicant__organisation__name, proposal__proxy_applicant__email, proposal__proxy_applicant__first_name, proposal__proxy_applicant__last_name',
                    },
                    {
                        data: 'processing_status',
                        name: 'processing_status',
                    },
                    {
                        data: 'proposal_lodgement_date',
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            return data != '' && data != null
                                ? moment(data).format(vm.dateFormat)
                                : '';
                        },
                        name: 'proposal__lodgement_date',
                    },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            let links = '';
                            links += full.district_assessor_can_assess
                                ? `<a href='/internal/proposal/${full.proposal}/district_proposal/${full.id}'>Process</a><br/>`
                                : `<a href='/internal/proposal/${full.proposal}/district_proposal/${full.id}'>View</a><br/>`;
                            return links;
                        },
                        searchable: false,
                        orderable: false,
                        name: '',
                    },
                    { data: 'proposal', visible: false },
                    { data: 'id', visible: false },
                ],
                processing: true,
            },
        };
    },
    computed: {},
    watch: {
        filterProposalStatus: function () {
            let vm = this;
            if (vm.filterProposalStatus != 'All') {
                vm.$refs.proposal_datatable.vmDataTable
                    .columns(3)
                    .search(vm.filterProposalStatus)
                    .draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable
                    .columns(3)
                    .search('')
                    .draw();
            }
        },

        filterProposalRegion: function () {
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterProposalSubmitter: function () {
            let vm = this;
            if (vm.filterProposalSubmitter != 'All') {
                vm.$refs.proposal_datatable.vmDataTable
                    .columns(1)
                    .search(vm.filterProposalSubmitter)
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
        let vm = this;
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
    },
    methods: {
        fetchFilterLists: function () {
            let vm = this;

            vm.$http.get(api_endpoints.filter_list_district_proposals).then(
                (response) => {
                    vm.proposal_submitters = response.body.submitters;
                    vm.proposal_status =
                        response.body.processing_status_choices;
                },
                (error) => {
                    console.log(error);
                }
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
    },
};
</script>
<style scoped></style>
