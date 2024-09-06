<!-- eslint-disable vue/no-mutating-props -->
<template lang="html">
    <div class="row">
        <div class="col-sm-12">
            <div class="col-md-12">
                <div class="row">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            <h3 class="panel-title">
                                Applicant
                                <a
                                    class="panelClicker"
                                    :href="'#' + detailsBody"
                                    data-toggle="collapse"
                                    data-parent="#userInfo"
                                    expanded="true"
                                    :aria-controls="detailsBody"
                                >
                                    <span
                                        class="glyphicon glyphicon-chevron-up pull-right"
                                    ></span>
                                </a>
                            </h3>
                        </div>
                        <div
                            v-if="applicantType == 'ORG'"
                            :id="detailsBody"
                            class="panel-body panel-collapse collapse in"
                        >
                            <form class="form-horizontal">
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label"
                                        >Name</label
                                    >
                                    <div class="col-sm-6">
                                        <input
                                            v-model="
                                                proposal.org_applicant.name
                                            "
                                            disabled
                                            type="text"
                                            class="form-control"
                                            name="applicantName"
                                            placeholder=""
                                            style="width: 100%"
                                        />
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label"
                                        >Trading Name</label
                                    >
                                    <div class="col-sm-6">
                                        <input
                                            v-model="
                                                proposal.org_applicant
                                                    .trading_name
                                            "
                                            disabled
                                            type="text"
                                            class="form-control"
                                            name="applicantName"
                                            placeholder=""
                                            style="width: 100%"
                                        />
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label"
                                        >ABN/ACN</label
                                    >
                                    <div class="col-sm-6">
                                        <input
                                            v-model="proposal.org_applicant.abn"
                                            disabled
                                            type="text"
                                            class="form-control"
                                            name="applicantABN"
                                            placeholder=""
                                            style="width: 100%"
                                        />
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div
                            v-if="applicantType == 'SUB'"
                            :id="detailsBody"
                            class="panel-body panel-collapse collapse in"
                        >
                            <form class="form-horizontal">
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label"
                                        >Given Name(s)</label
                                    >
                                    <div class="col-sm-6">
                                        <input
                                            v-model="
                                                proposal.submitter.first_name
                                            "
                                            disabled
                                            type="text"
                                            class="form-control"
                                            name="applicantName"
                                            placeholder=""
                                        />
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label"
                                        >Surname</label
                                    >
                                    <div class="col-sm-6">
                                        <input
                                            v-model="
                                                proposal.submitter.last_name
                                            "
                                            disabled
                                            type="text"
                                            class="form-control"
                                            name="applicantName"
                                            placeholder=""
                                        />
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-12">
                <div class="row">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            <h3 class="panel-title">
                                Address Details
                                <a
                                    class="panelClicker"
                                    :href="'#' + addressBody"
                                    data-toggle="collapse"
                                    data-parent="#userInfo"
                                    expanded="false"
                                    :aria-controls="addressBody"
                                >
                                    <span
                                        class="glyphicon glyphicon-chevron-down pull-right"
                                    ></span>
                                </a>
                            </h3>
                        </div>
                        <div
                            v-if="
                                applicantType == 'ORG' &&
                                proposal.org_applicant.address
                            "
                            :id="addressBody"
                            class="panel-body panel-collapse collapse"
                        >
                            <form class="form-horizontal">
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label"
                                        >Street</label
                                    >
                                    <div class="col-sm-6">
                                        <input
                                            v-model="
                                                proposal.org_applicant.address
                                                    .line1
                                            "
                                            disabled
                                            type="text"
                                            class="form-control"
                                            name="street"
                                            placeholder=""
                                        />
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label"
                                        >Town/Suburb</label
                                    >
                                    <div class="col-sm-6">
                                        <input
                                            v-model="
                                                proposal.org_applicant.address
                                                    .locality
                                            "
                                            disabled
                                            type="text"
                                            class="form-control"
                                            name="surburb"
                                            placeholder=""
                                        />
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label"
                                        >State</label
                                    >
                                    <div class="col-sm-2">
                                        <input
                                            v-model="
                                                proposal.org_applicant.address
                                                    .state
                                            "
                                            disabled
                                            type="text"
                                            class="form-control"
                                            name="country"
                                            placeholder=""
                                        />
                                    </div>
                                    <label for="" class="col-sm-2 control-label"
                                        >Postcode</label
                                    >
                                    <div class="col-sm-2">
                                        <input
                                            v-model="
                                                proposal.org_applicant.address
                                                    .postcode
                                            "
                                            disabled
                                            type="text"
                                            class="form-control"
                                            name="postcode"
                                            placeholder=""
                                        />
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label"
                                        >Country</label
                                    >
                                    <div class="col-sm-4">
                                        <input
                                            v-model="
                                                proposal.org_applicant.address
                                                    .country
                                            "
                                            disabled
                                            type="text"
                                            class="form-control"
                                            name="country"
                                        />
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div
                            v-if="
                                applicantType == 'SUB' &&
                                proposal.submitter.residential_address
                            "
                            :id="addressBody"
                            class="panel-body panel-collapse collapse"
                        >
                            <form class="form-horizontal">
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label"
                                        >Street</label
                                    >
                                    <div class="col-sm-6">
                                        <input
                                            v-model="
                                                proposal.submitter
                                                    .residential_address.line1
                                            "
                                            disabled
                                            type="text"
                                            class="form-control"
                                            name="street"
                                            placeholder=""
                                        />
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label"
                                        >Town/Suburb</label
                                    >
                                    <div class="col-sm-6">
                                        <input
                                            v-model="
                                                proposal.submitter
                                                    .residential_address
                                                    .locality
                                            "
                                            disabled
                                            type="text"
                                            class="form-control"
                                            name="surburb"
                                            placeholder=""
                                        />
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label"
                                        >State</label
                                    >
                                    <div class="col-sm-2">
                                        <input
                                            v-model="
                                                proposal.submitter
                                                    .residential_address.state
                                            "
                                            disabled
                                            type="text"
                                            class="form-control"
                                            name="country"
                                            placeholder=""
                                        />
                                    </div>
                                    <label for="" class="col-sm-2 control-label"
                                        >Postcode</label
                                    >
                                    <div class="col-sm-2">
                                        <input
                                            v-model="
                                                proposal.submitter
                                                    .residential_address
                                                    .postcode
                                            "
                                            disabled
                                            type="text"
                                            class="form-control"
                                            name="postcode"
                                            placeholder=""
                                        />
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label"
                                        >Country</label
                                    >
                                    <div class="col-sm-4">
                                        <input
                                            v-model="
                                                proposal.submitter
                                                    .residential_address.country
                                            "
                                            disabled
                                            type="text"
                                            class="form-control"
                                            name="country"
                                        />
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-12">
                <div class="row">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            <h3 class="panel-title">
                                Contact Details
                                <a
                                    class="panelClicker"
                                    :href="'#' + contactsBody"
                                    data-toggle="collapse"
                                    data-parent="#userInfo"
                                    expanded="false"
                                    :aria-controls="contactsBody"
                                >
                                    <span
                                        class="glyphicon glyphicon-chevron-down pull-right"
                                    ></span>
                                </a>
                            </h3>
                        </div>
                        <div
                            v-if="applicantType == 'ORG'"
                            :id="contactsBody"
                            class="panel-body panel-collapse collapse"
                        >
                            <table
                                :id="contacts_table_id"
                                ref="contacts_datatable"
                                class="hover table table-striped table-bordered dt-responsive"
                                cellspacing="0"
                                width="100%"
                            ></table>
                        </div>
                        <div
                            v-if="applicantType == 'SUB'"
                            :id="contactsBody"
                            class="panel-body panel-collapse collapse"
                        >
                            <form class="form-horizontal">
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label"
                                        >Phone (work)</label
                                    >
                                    <div class="col-sm-6">
                                        <input
                                            v-model="
                                                proposal.submitter.phone_number
                                            "
                                            disabled
                                            type="text"
                                            class="form-control"
                                            name="applicantPhoneNumber"
                                            placeholder=""
                                        />
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label"
                                        >Mobile</label
                                    >
                                    <div class="col-sm-6">
                                        <input
                                            v-model="
                                                proposal.submitter.mobile_number
                                            "
                                            disabled
                                            type="text"
                                            class="form-control"
                                            name="applicantMobileNumber"
                                            placeholder=""
                                        />
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label"
                                        >Email</label
                                    >
                                    <div class="col-sm-6">
                                        <input
                                            v-model="proposal.submitter.email"
                                            disabled
                                            type="text"
                                            class="form-control"
                                            name="applicantEmail"
                                            placeholder=""
                                        />
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { api_endpoints, helpers } from '@/utils/hooks';
export default {
    name: 'ApplicantComponent',
    components: {},
    props: {
        proposal: {
            type: Object,
            required: true,
        },
    },
    data: function () {
        let vm = this;
        return {
            values: null,
            detailsBody: 'detailsBody' + vm._uid,
            addressBody: 'addressBody' + vm._uid,
            contactsBody: 'contactsBody' + vm._uid,
            panelClickersInitialised: false,
            contacts_table_id: vm._uid + 'contacts-table',
            contacts_table_initialised: false,
            contacts_options: {
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>",
                },
                responsive: true,
                ajax: {
                    url: vm.contactsURL,
                    dataSrc: '',
                },
                columns: [
                    {
                        title: 'Name',
                        mRender: function (data, type, full) {
                            return full.first_name + ' ' + full.last_name;
                        },
                    },
                    {
                        title: 'Phone',
                        data: 'phone_number',
                    },
                    {
                        title: 'Mobile',
                        data: 'mobile_number',
                    },
                    {
                        title: 'Fax',
                        data: 'fax_number',
                    },
                    {
                        title: 'Email',
                        data: 'email',
                    },
                ],
                processing: true,
            },
            contacts_table: null,
        };
    },
    computed: {
        contactsURL: function () {
            return this.proposal != null
                ? helpers.add_endpoint_json(
                      api_endpoints.organisations,
                      this.proposal.org_applicant.id + '/contacts'
                  )
                : '';
        },
        applicantType: function () {
            return this.proposal.applicant_type;
        },
    },
    mounted: function () {
        let vm = this;
        if (!vm.panelClickersInitialised) {
            $('.panelClicker[data-toggle="collapse"]').on('click', function () {
                var chev = $(this).children()[0];
                window.setTimeout(function () {
                    $(chev).toggleClass(
                        'glyphicon-chevron-down glyphicon-chevron-up'
                    );
                }, 100);
            });
            vm.panelClickersInitialised = true;
        }
        this.$nextTick(() => {
            vm.initialiseOrgContactTable();
        });
    },
    methods: {
        initialiseOrgContactTable: function () {
            let vm = this;
            if (vm.proposal && !vm.contacts_table_initialised) {
                vm.contacts_options.ajax.url = helpers.add_endpoint_json(
                    api_endpoints.organisations,
                    vm.proposal.org_applicant.id + '/contacts'
                );
                vm.contacts_table = $('#' + vm.contacts_table_id).DataTable(
                    vm.contacts_options
                );
                vm.contacts_table_initialised = true;
            }
        },
    },
};
</script>

<style lang="css" scoped></style>
