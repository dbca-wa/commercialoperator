<template>
    <div id="internalOrgAccessDash" class="container">
        <div class="row">
            <div class="col-sm-12">
                <FormSection
                    :form-collapse="false"
                    label="Organisation Access Requests"
                    index="organisation_access_requests"
                >
                    <div class="panel panel-default">
                        <div class="row mb-1">
                            <div class="col-md-3">
                                <div
                                    id="select_organisation_access_organisation_parent"
                                    class="form-group"
                                >
                                    <label
                                        for="select_organisation_access_organisation"
                                        >Organisation</label
                                    >
                                    <div v-show="isLoading">
                                        <select class="form-control">
                                            <option value="">Loading...</option>
                                        </select>
                                    </div>
                                    <div v-show="!isLoading">
                                        <select
                                            id="select_organisation_access_organisation"
                                            ref="select_organisation_access_organisation"
                                            v-model="filterOrganisation"
                                            class="form-control"
                                        >
                                            <option value="All">All</option>
                                            <option
                                                v-for="o in organisationChoices"
                                                :key="o"
                                                :value="o"
                                            >
                                                {{ o }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div
                                    id="select_organisation_access_applicant_parent"
                                    class="form-group"
                                >
                                    <label
                                        for="select_organisation_access_applicant"
                                        >Applicant</label
                                    >
                                    <div v-show="isLoading">
                                        <select class="form-control">
                                            <option value="">Loading...</option>
                                        </select>
                                    </div>
                                    <div v-show="!isLoading">
                                        <select
                                            id="select_organisation_access_applicant"
                                            ref="select_organisation_access_applicant"
                                            v-model="filterApplicant"
                                            class="form-control"
                                        >
                                            <option value="All">All</option>
                                            <option
                                                v-for="a in applicantChoices"
                                                :key="a"
                                                :value="a"
                                            >
                                                {{ a }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div
                                    id="select_organisation_access_role_parent"
                                    class="form-group"
                                >
                                    <label for="select_organisation_access_role"
                                        >Role</label
                                    >
                                    <div v-show="isLoading">
                                        <select class="form-control">
                                            <option value="">Loading...</option>
                                        </select>
                                    </div>
                                    <div v-show="!isLoading">
                                        <select
                                            id="select_organisation_access_role"
                                            ref="select_organisation_access_role"
                                            v-model="filterRole"
                                            class="form-control"
                                        >
                                            <option value="All">All</option>
                                            <option
                                                v-for="r in roleChoices"
                                                :key="r"
                                                :value="r"
                                            >
                                                {{ r }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div
                                    id="select_organisation_access_status_parent"
                                    class="form-group"
                                >
                                    <label
                                        for="select_organisation_access_status"
                                        >Status</label
                                    >
                                    <div v-show="isLoading">
                                        <select class="form-control">
                                            <option value="">Loading...</option>
                                        </select>
                                    </div>
                                    <div v-show="!isLoading">
                                        <select
                                            id="select_organisation_access_status"
                                            ref="select_organisation_access_status"
                                            v-model="filterStatus"
                                            class="form-control"
                                        >
                                            <option value="All">All</option>
                                            <option
                                                v-for="s in statusChoices"
                                                :key="s"
                                                :value="s"
                                            >
                                                {{ s }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <datatable
                                id="org-access-table"
                                ref="org_access_table"
                                :dt-options="dtOptions"
                                :dt-headers="dtHeaders"
                            ></datatable>
                        </div>
                    </div>
                </FormSection>
            </div>
        </div>
    </div>
</template>
<script>
import Vue from 'vue';
import $ from 'jquery';
import FormSection from '@/components/forms/section_toggle.vue';
import datatable from '@vue-utils/datatable.vue';
import { api_endpoints, helpers } from '@/utils/hooks';
export default {
    name: 'OrganisationAccessDashboard',
    components: {
        FormSection,
        datatable,
    },
    data() {
        let vm = this;
        return {
            // Filters
            pBody: 'pBody' + vm._uid,
            filterOrganisation: 'All',
            filterApplicant: 'All',
            filterRole: 'All',
            filterStatus: 'All',
            organisationChoices: [],
            applicantChoices: [],
            statusChoices: [],
            roleChoices: [],
            members: [],
            profile: {},
            dtOptions: {
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>",
                },
                responsive: true,
                serverSide: true,
                processing: true,
                order: [[0, 'desc']],
                ajax: {
                    url: api_endpoints.organisation_requests_datatable,
                    dataSrc: 'data',
                    data: function (d) {
                        d.filter_organisation = vm.filterOrganisation;
                        d.filter_applicant = vm.filterApplicant;
                        d.filter_role = vm.filterRole;
                        d.filter_status = vm.filterStatus;

                        return d;
                    },
                },
                columns: [
                    {
                        data: 'id',
                    },
                    {
                        data: 'name',
                    },
                    {
                        data: 'requester',
                    },
                    {
                        data: 'role',
                    },
                    {
                        data: 'status',
                    },
                    {
                        data: 'lodgement_date',
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            return moment(data).format('DD/MM/YYYY');
                        },
                    },
                    {
                        data: 'assigned_officer',
                    },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            let column;
                            if (
                                full.status == 'Approved' ||
                                full.status == 'Declined'
                            ) {
                                column =
                                    "<a href='/internal/organisations/access/__ID__' >View </a>";
                            } else {
                                if (vm.is_assessor) {
                                    column =
                                        "<a href='/internal/organisations/access/__ID__'> Process </a>";
                                } else {
                                    column =
                                        "<a href='/internal/organisations/access/__ID__' >View </a>";
                                }
                            }
                            return column.replace(/__ID__/g, data);
                        },
                    },
                ],
                initComplete: function () {
                    // Grab Organisation from the data in the table
                    var organisationColumn =
                        vm.$refs.org_access_table.vmDataTable.columns(1);
                    organisationColumn
                        .data()
                        .unique()
                        // eslint-disable-next-line no-unused-vars
                        .each(function (d, j) {
                            let organisationChoices = [];
                            $.each(d, (index, a) => {
                                a != null && organisationChoices.indexOf(a) < 0
                                    ? organisationChoices.push(a)
                                    : '';
                            });
                            // Case insensitive sort in place
                            vm.organisationChoices = organisationChoices.sort(
                                (a, b) =>
                                    a.localeCompare(b, 'en', {
                                        sensitivity: 'base',
                                    })
                            );
                        });
                    // Grab Applicant from the data in the table
                    var applicantColumn =
                        vm.$refs.org_access_table.vmDataTable.columns(2);
                    applicantColumn
                        .data()
                        .unique()
                        // eslint-disable-next-line no-unused-vars
                        .each(function (d, j) {
                            let applicationChoices = [];
                            $.each(d, (index, a) => {
                                a = a.trim();
                                [null, ''].includes(a) == false &&
                                applicationChoices.indexOf(a) < 0
                                    ? applicationChoices.push(a)
                                    : '';
                            });
                            // Case insensitive sort in place
                            vm.applicantChoices = applicationChoices.sort(
                                (a, b) =>
                                    a.localeCompare(b, 'en', {
                                        sensitivity: 'base',
                                    })
                            );
                        });
                    // Grab Role from the data in the table
                    var roleColumn =
                        vm.$refs.org_access_table.vmDataTable.columns(3);
                    roleColumn
                        .data()
                        .unique()
                        // eslint-disable-next-line no-unused-vars
                        .each(function (d, j) {
                            let roleChoices = [];
                            $.each(d, (index, a) => {
                                a != null && roleChoices.indexOf(a) < 0
                                    ? roleChoices.push(a)
                                    : '';
                            });
                            vm.roleChoices = roleChoices.sort();
                        });
                    // Grab Status from the data in the table
                    var statusColumn =
                        vm.$refs.org_access_table.vmDataTable.columns(4);
                    statusColumn
                        .data()
                        .unique()
                        // eslint-disable-next-line no-unused-vars
                        .each(function (d, j) {
                            let statusChoices = [];
                            $.each(d, (index, a) => {
                                a != null && statusChoices.indexOf(a) < 0
                                    ? statusChoices.push(a)
                                    : '';
                            });
                            vm.statusChoices = statusChoices.sort();
                        });

                    vm.isLoading = false;
                },
            },
            dtHeaders: [
                'Request Number',
                'Organisation',
                'Applicant',
                'Role',
                'Status',
                'Lodged on',
                'Assigned To',
                'Action',
            ],
            isLoading: false,
        };
    },
    watch: {
        filterOrganisation: function () {
            let vm = this;
            if (vm.filterOrganisation != 'All') {
                vm.$refs.org_access_table.vmDataTable
                    .columns(1)
                    .search(vm.filterOrganisation)
                    .draw();
            } else {
                vm.$refs.org_access_table.vmDataTable
                    .columns(1)
                    .search('')
                    .draw();
            }
        },
        filterApplicant: function () {
            let vm = this;
            if (vm.filterApplicant != 'All') {
                vm.$refs.org_access_table.vmDataTable
                    .columns(2)
                    .search(vm.filterApplicant)
                    .draw();
            } else {
                vm.$refs.org_access_table.vmDataTable
                    .columns(2)
                    .search('')
                    .draw();
            }
        },
        filterRole: function () {
            let vm = this;
            if (vm.filterRole != 'All') {
                vm.$refs.org_access_table.vmDataTable
                    .columns(3)
                    .search(vm.filterRole)
                    .draw();
            } else {
                vm.$refs.org_access_table.vmDataTable
                    .columns(3)
                    .search('')
                    .draw();
            }
        },
        filterStatus: function () {
            let vm = this;
            if (vm.filterStatus != 'All') {
                vm.$refs.org_access_table.vmDataTable
                    .columns(4)
                    .search(vm.filterStatus)
                    .draw();
            } else {
                vm.$refs.org_access_table.vmDataTable
                    .columns(4)
                    .search('')
                    .draw();
            }
        },
    },
    mounted: function () {
        this.isLoading = true;
        this.fetchAccessGroupMembers();
        this.fetchProfile();
        this.$nextTick(() => {
            this.addEventListeners();
        });
    },
    methods: {
        is_assessor: function () {
            return this.check_assessor();
        },

        fetchAccessGroupMembers: function () {
            let vm = this;
            vm.$http.get(api_endpoints.organisation_access_group_members).then(
                (response) => {
                    vm.members = response.body;
                },
                (error) => {
                    console.log(error);
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
        check_assessor: function () {
            let vm = this;
            var assessor = vm.members.filter(function (elem) {
                return elem.name == vm.profile.full_name;
            });
            if (assessor.length > 0) return true;
            else return false;
        },
        addEventListeners: function () {
            helpers.initialiseSelect2.bind(this)(
                'select_organisation_access_organisation',
                'select_organisation_access_organisation_parent',
                'filterOrganisation',
                'Select Organisation',
                false
            );
            helpers.initialiseSelect2.bind(this)(
                'select_organisation_access_applicant',
                'select_organisation_access_applicant_parent',
                'filterApplicant',
                'Select Applicant',
                false
            );
            helpers.initialiseSelect2.bind(this)(
                'select_organisation_access_role',
                'select_organisation_access_role_parent',
                'filterRole',
                'Select Role',
                false
            );
            helpers.initialiseSelect2.bind(this)(
                'select_organisation_access_status',
                'select_organisation_access_status_parent',
                'filterStatus',
                'Select Status',
                false
            );
        },
    },
};
</script>
