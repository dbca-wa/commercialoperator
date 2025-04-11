<template>
    <!-- <div v-if="email_user" class="card"> -->
    <div class="card">
        <div class="card-header fw-bold h4" style="padding: 30px">
            <div class="row">
                <div class="col-6">Organisations</div>
                <div class="col-6 text-end">
                    <i
                        class="bi fw-bold chevron-toggle down-chevron-open"
                        data-bs-target="#organisations-tab-body"
                        onclick=""
                    ></i>
                </div>
            </div>
        </div>
        <div id="organisations-tab-body" class="card-body">
            <FormSection
                :form-collapse="false"
                label="Linked User Accounts"
                index="linked_user_accounts"
                subtitle="Manage the user accounts linked to the organisation"
            >
                <div class="row">
                    <div class="col-sm-12">
                        <div class="row">
                            <div class="col-sm-12">
                                <h4>Persons linked to this organisation:</h4>
                            </div>
                            <div v-for="d in org.delegates" :key="d.id">
                                <div v-if="d.is_admin" class="col-sm-6">
                                    <h4>
                                        {{ d.name }}
                                        ({{ d.email }}
                                        - Admin)
                                    </h4>
                                </div>
                                <div v-else class="col-sm-6">
                                    <h4>
                                        {{ d.name }}
                                        ({{ d.email }})
                                    </h4>
                                </div>
                            </div>
                            <div class="col-sm-12 top-buffer-s mb-3">
                                <strong
                                    >Persons linked to the organisation are
                                    controlled by the organisation. The
                                    Department cannot manage this list of
                                    people.</strong
                                >
                            </div>
                        </div>
                    </div>
                </div>

                <form
                    v-if="org.pins"
                    class="form-horizontal"
                    action="index.html"
                    method="post"
                >
                    <div class="row">
                        <div class="col-sm-6">
                            <div class="form-group row mb-3">
                                <label for="" class="col-sm-6 control-label">
                                    Organisation User Pin Code 1:</label
                                >
                                <div class="col-sm-6">
                                    <label class="control-label">{{
                                        org.pins.three
                                    }}</label>
                                </div>
                            </div>
                            <div class="form-group row mb-3">
                                <label for="" class="col-sm-6 control-label"
                                    >Organisation User Pin Code 2:</label
                                >
                                <div class="col-sm-6">
                                    <label class="control-label">{{
                                        org.pins.four
                                    }}</label>
                                </div>
                            </div>
                        </div>
                        <div class="col-sm-6">
                            <div class="form-group row mb-3">
                                <label for="" class="col-sm-6 control-label">
                                    Organisation Administrator Pin Code
                                    1:</label
                                >
                                <div class="col-sm-6">
                                    <label class="control-label">{{
                                        org.pins.one
                                    }}</label>
                                </div>
                            </div>
                            <div class="form-group row mb-3">
                                <label for="" class="col-sm-6 control-label"
                                    >Organisation Administrator Pin Code
                                    2:</label
                                >
                                <div class="col-sm-6">
                                    <label class="control-label">{{
                                        org.pins.two
                                    }}</label>
                                </div>
                            </div>
                        </div>
                    </div>
                </form>
                <div>
                    <datatable
                        id="organisation_contacts_datatable_ref"
                        ref="contacts_datatable_user"
                        v-model="filterOrgContactStatus"
                        :dt-options="contacts_options_ref"
                        :dt-headers="contacts_headers_ref"
                    />
                </div>
            </FormSection>
        </div>
    </div>
</template>

<script>
import { api_endpoints, constants, helpers, utils } from '@/utils/hooks';
import alert from '@vue-utils/alert.vue';
import datatable from '@vue-utils/datatable.vue';
import FormSection from '@/components/forms/section_toggle.vue';

export default {
    name: 'OrganisationComponent',
    components: {
        alert,
        datatable,
        FormSection,
    },
    beforeRouteEnter: function (to, from, next) {
        let initialisers = [
            // utils.fetchCountries(),
            // utils.fetchOrganisation(to.params.org_id),
            utils.fetchProfile(),
        ];
        Promise.all(initialisers).then((data) => {
            next((vm) => {
                // vm.countries = data[0];
                // vm.org = data[1];
                // vm.profile = data[2];
                vm.profile = data[0];
                vm.org.organisation_address =
                    vm.org.organisation_address != null
                        ? vm.org.organisation_address
                        : {};
                vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
                vm.is_commercialoperator_admin =
                    vm.profile.is_commercialoperator_admin;
                vm.is_org_access_member = vm.profile.is_org_access_member;
            });
        });
    },
    data() {
        const vm = this;
        return {
            api_endpoints: api_endpoints,
            email_user: null,
            selectedOrganisation: null,
            newOrganisation: null,
            organisation_requests: null,
            validatePinsError: null,
            validatingPins: false,
            pins: {
                pin1: '',
                pin2: '',
            },
            helpers: helpers,
            org: {},
            contacts_headers_ref: ['Name', 'Role', 'Email', 'Status', 'Action'],
            contacts_options_ref: {
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>",
                },
                responsive: true,
                ajax: {
                    url: helpers.add_endpoint_json(
                        api_endpoints.organisations,
                        vm.$route.params.org_id + '/contacts_exclude'
                    ),

                    dataSrc: '',
                },
                columns: [
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            return full.first_name + ' ' + full.last_name;
                        },
                    },
                    { data: 'user_role' },
                    { data: 'email' },
                    { data: 'user_status' },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            let links = '';
                            if (vm.is_commercialoperator_admin) {
                                if (full.user_status == 'Pending') {
                                    links += `<a data-email='${full.email}' data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="accept_contact">Accept</a><br/>`;
                                    links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="decline_contact">Decline</a><br/>`;
                                } else if (full.user_status == 'Suspended') {
                                    links += `<a data-email='${full.email}' data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="reinstate_contact">Reinstate</a><br/>`;
                                } else if (full.user_status == 'Active') {
                                    links += `<a data-email='${full.email}' data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="unlink_contact">Unlink</a><br/>`;
                                    links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="suspend_contact">Suspend</a><br/>`;
                                    if (full.user_role == 'Organisation User') {
                                        links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="make_admin_contact">Make Organisation Admin</a><br/>`;
                                    } else {
                                        links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="make_user_contact">Make Organisation User</a><br/>`;
                                    }
                                } else if (full.user_status == 'Unlinked') {
                                    links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="relink_contact">Reinstate</a><br/>`;
                                } else if (full.user_status == 'Declined') {
                                    links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="accept_declined_contact">Accept (Previously Declined)</a><br/>`;
                                }
                            }
                            return links;
                        },
                    },
                ],
                processing: true,
            },
            filterOrgContactStatus: null,
            is_commercialoperator_admin: false,
        };
    },
    computed: {
        linkOrganisationTitle: function () {
            if (
                this.organisation_requests &&
                this.organisation_requests.length
            ) {
                return 'Link another Organisation';
            }
            return 'Link an organisation';
        },
        csrf_token: function () {
            return helpers.getCookie('csrftoken');
        },
    },
    created: function () {
        console.log('account.vue created');
        // this.fetchInitialData();
    },
    mounted: function () {
        console.log('account.vue mounted');
    },
    methods: {},
};
</script>

<style scoped></style>
