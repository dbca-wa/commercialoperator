<!-- eslint-disable vue/no-mutating-props -->
<template lang="html">
    <div id="otherInfo" class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">
                        Pre-Event Training<small></small>
                        <a
                            class="panelClicker"
                            :href="'#' + lBody"
                            data-toggle="collapse"
                            data-parent="#otherInfo"
                            :expanded="true"
                            :aria-controls="lBody"
                        >
                            <span
                                class="glyphicon glyphicon-chevron-up pull-right"
                            ></span>
                        </a>
                    </h3>
                </div>
                <div :id="lBody" class="panel-body collapse in">
                    <div class="">
                        <div class="form-horizontal col-sm-12 borderDecoration">
                            <div class="">
                                <div class="row">
                                    <div class="col-sm-6">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Date of Pre-event training
                                        </label>
                                    </div>
                                    <div class="col-sm-6">
                                        <div
                                            ref="training_date"
                                            class="input-group date"
                                            style="width: 70%"
                                        >
                                            <input
                                                v-model="
                                                    proposal.event_other_details
                                                        .training_date
                                                "
                                                type="text"
                                                class="form-control"
                                                name="training_date"
                                                placeholder="DD/MM/YYYY"
                                                :disabled="proposal.readonly"
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
                        </div>

                        <div class="form-horizontal col-sm-12 borderDecoration">
                            <div class="">
                                <div class="row">
                                    <label class="col-sm-12" for="Name"
                                        >List the parks (terrestrial and/or
                                        marine) where this Pre-event training is
                                        proposed to occur. Please attach a
                                        detailed itinerary</label
                                    >
                                    <PreEventParksTable
                                        ref="pre_event_parks_table"
                                        :url="pre_event_parks_url"
                                        :proposal="proposal"
                                    ></PreEventParksTable>
                                </div>
                                <div class="row">&nbsp;</div>
                            </div>
                        </div>

                        <div class="form-horizontal col-sm-12 borderDecoration">
                            <div class="">
                                <div class="row">
                                    <div class="col-sm-6">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Number of Participants
                                            expected</label
                                        >
                                    </div>
                                    <div class="col-sm-6">
                                        <div
                                            ref="participants_number"
                                            class="input-group date"
                                            style="width: 70%"
                                        >
                                            <input
                                                v-model="
                                                    proposal.event_other_details
                                                        .participants_number
                                                "
                                                type="number"
                                                class="form-control"
                                                name="participants_number"
                                                :disabled="
                                                    proposal.readonly ||
                                                    proposal.pending_amendment_request ||
                                                    proposal.is_amendment_proposal
                                                "
                                                onkeydown="return event.keyCode !== 69 && event.keyCode !== 187 && event.keyCode !== 189"
                                                @paste.prevent
                                            />
                                        </div>
                                    </div>
                                </div>
                                <div class="row">&nbsp;</div>
                                <div class="row">
                                    <div class="col-sm-6">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Number of officials</label
                                        >
                                    </div>
                                    <div class="col-sm-6">
                                        <div
                                            ref="officials_number"
                                            class="input-group date"
                                            style="width: 70%"
                                        >
                                            <input
                                                v-model="
                                                    proposal.event_other_details
                                                        .officials_number
                                                "
                                                type="number"
                                                class="form-control"
                                                name="officials_number"
                                                :disabled="
                                                    proposal.readonly ||
                                                    proposal.pending_amendment_request ||
                                                    proposal.is_amendment_proposal
                                                "
                                                onkeydown="return event.keyCode !== 69 && event.keyCode !== 187 && event.keyCode !== 189"
                                                @paste.prevent
                                            />
                                        </div>
                                    </div>
                                </div>
                                <div class="row">&nbsp;</div>
                                <div class="row">
                                    <div class="col-sm-6">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Number of support vehicles/
                                            vessels</label
                                        >
                                    </div>
                                    <div class="col-sm-6">
                                        <div
                                            ref="support_vehicle_number"
                                            class="input-group date"
                                            style="width: 70%"
                                        >
                                            <input
                                                v-model="
                                                    proposal.event_other_details
                                                        .support_vehicle_number
                                                "
                                                type="number"
                                                class="form-control"
                                                name="support_vehicle_number"
                                                :disabled="
                                                    proposal.readonly ||
                                                    proposal.pending_amendment_request ||
                                                    proposal.is_amendment_proposal
                                                "
                                                onkeydown="return event.keyCode !== 69 && event.keyCode !== 187 && event.keyCode !== 189"
                                                @paste.prevent
                                            />
                                        </div>
                                    </div>
                                </div>
                                <div class="row">&nbsp;</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">
                        Other <small></small>
                        <a
                            class="panelClicker"
                            :href="'#' + oBody"
                            data-toggle="collapse"
                            data-parent="#userInfo"
                            :expanded="true"
                            :aria-controls="oBody"
                        >
                            <span
                                class="glyphicon glyphicon-chevron-up pull-right"
                            ></span>
                        </a>
                    </h3>
                </div>
                <div :id="oBody" class="panel-body collapse in">
                    <div class="">
                        <div class="form-horizontal col-sm-12">
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <label
                                            >Provide any additional information
                                            to support your application. If you
                                            would like to access a park that is
                                            not listed in the previous sections,
                                            please include here.</label
                                        >
                                    </div>
                                </div>
                                <div class="row">
                                    <div
                                        class="col-sm-12"
                                        style="margin-bottom: 5px"
                                    >
                                        <textarea
                                            v-model="
                                                proposal.event_other_details
                                                    .other_comments
                                            "
                                            class="form-control"
                                            :disabled="proposal.readonly"
                                        ></textarea>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-sm-12">
                                        <FileField
                                            :id="'proposal' + proposal.id"
                                            :proposal_id="proposal.id"
                                            :is-repeatable="true"
                                            name="event_other_details"
                                            :readonly="!canEditActivities"
                                        ></FileField>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">
                        Payment of Fees and Charges<small></small>
                        <a
                            class="panelClicker"
                            :href="'#' + mBody"
                            data-toggle="collapse"
                            data-parent="#userInfo"
                            :expanded="true"
                            :aria-controls="mBody"
                        >
                            <span
                                class="glyphicon glyphicon-chevron-up pull-right"
                            ></span>
                        </a>
                    </h3>
                </div>
                <div :id="mBody" class="panel-body collapse in">
                    <div class="">
                        <div class="form-horizontal col-sm-12">
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <label
                                            >Please note a licence charge
                                            applies to commercial events which
                                            is payable in addition to the
                                            application fees. Please see the
                                            department
                                            <a
                                                :href="fees_and_charges"
                                                target="_blank"
                                                >website</a
                                            >
                                            for further information on
                                            applicable fees and charges and how
                                            they are paid.</label
                                        >
                                    </div>
                                </div>
                                <div class="row">&nbsp;</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">
                        Insurance <small></small>
                        <a
                            class="panelClicker"
                            :href="'#' + iBody"
                            data-toggle="collapse"
                            data-parent="#userInfo"
                            :expanded="true"
                            :aria-controls="iBody"
                        >
                            <span
                                class="glyphicon glyphicon-chevron-up pull-right"
                            ></span>
                        </a>
                    </h3>
                </div>
                <div :id="iBody" class="panel-body collapse in">
                    <div class="">
                        <div class="form-horizontal col-sm-12">
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <label>
                                            <ol type="a">
                                                <li>
                                                    Attach your policy for
                                                    public liability insurance
                                                    that covers the areas and
                                                    operations allowed under the
                                                    licence, and in the name of
                                                    the applicant to the extent
                                                    of its rights and interests,
                                                    for a sum of not less than
                                                    AU$10 million per event.
                                                </li>
                                                <li>
                                                    It is a requirement of all
                                                    licenced operators to
                                                    maintain appropriate public
                                                    liability insurance.
                                                </li>
                                            </ol></label
                                        >
                                    </div>
                                </div>

                                <div class="row">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Certificate of currency
                                        </label>
                                    </div>
                                    <div class="col-sm-3">
                                        <FileField
                                            :id="'proposal' + proposal.id"
                                            ref="currency_doc"
                                            :proposal_id="proposal.id"
                                            :is-repeatable="false"
                                            name="currency_certificate"
                                            :readonly="!canEditActivities"
                                        ></FileField>
                                    </div>
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Expiry Date
                                        </label>
                                    </div>
                                    <div class="col-sm-3">
                                        <div
                                            ref="insurance_expiry"
                                            class="input-group date"
                                            style="width: 70%"
                                        >
                                            <input
                                                v-model="
                                                    proposal.event_other_details
                                                        .insurance_expiry
                                                "
                                                type="text"
                                                class="form-control"
                                                name="insurance_expiry"
                                                placeholder="DD/MM/YYYY"
                                                :disabled="proposal.readonly"
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
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">
                        Deed Poll<small></small>
                        <a
                            class="panelClicker"
                            :href="'#' + dBody"
                            data-toggle="collapse"
                            data-parent="#userInfo"
                            :expanded="true"
                            :aria-controls="dBody"
                        >
                            <span
                                class="glyphicon glyphicon-chevron-up pull-right"
                            ></span>
                        </a>
                    </h3>
                </div>
                <div :id="dBody" class="panel-body collapse in">
                    <div class="">
                        <div class="form-horizontal col-sm-12">
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <label
                                            >It is a requirement of all
                                            commercial operations licence
                                            holders to sign a deed poll to
                                            release and indemnify the State of
                                            Western Australia. Please note:
                                            electronic or digital signatures
                                            cannot be accepted.
                                        </label>
                                        <label v-if="deed_poll_url"
                                            >Please click
                                            <a
                                                :href="deed_poll_url"
                                                target="_blank"
                                                >here</a
                                            >
                                            to download the deed poll. The deed
                                            poll must be signed and have a
                                            witness signature and be dated. Once
                                            signed and dated, please scan and
                                            attach the deed poll below.</label
                                        >
                                        <label v-else
                                            >Please click here to download the
                                            deed poll. The deed poll must be
                                            signed and have a witness signature
                                            and be dated. Once signed and dated,
                                            please scan and attach the deed poll
                                            below.</label
                                        >
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-sm-12">
                                        <FileField
                                            :id="'proposal' + proposal.id"
                                            ref="deed_poll_doc"
                                            :proposal_id="proposal.id"
                                            :is-repeatable="false"
                                            name="deed_poll"
                                            :readonly="!canEditActivities"
                                        ></FileField>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import PreEventParksTable from './pre_event_parks_table.vue';
import FileField from '@/components/forms/filefield.vue';
import { api_endpoints, helpers } from '@/utils/hooks';
export default {
    components: {
        FileField,
        PreEventParksTable,
    },
    props: {
        proposal: {
            type: Object,
            required: true,
        },
        canEditActivities: {
            type: Boolean,
            default: true,
        },
    },
    data: function () {
        let vm = this;
        return {
            pBody: 'pBody' + vm._uid,
            lBody: 'lBody' + vm._uid,
            iBody: 'iBody' + vm._uid,
            mBody: 'mBody' + vm._uid,
            oBody: 'oBody' + vm._uid,
            cBody: 'cBody' + vm._uid,
            dBody: 'dBody' + vm._uid,
            values: null,
            accreditation_choices: [],
            accreditation_type: [],
            selected_accreditations: [],
            licence_period_choices: [],
            mooring: [''],
            global_settings: [],
            datepickerOptions: {
                format: 'DD/MM/YYYY',
                showClear: true,
                useCurrent: false,
                keepInvalid: true,
                allowInputToggle: true,
            },
            pre_event_parks_url: helpers.add_endpoint_json(
                api_endpoints.proposals,
                vm.$route.params.proposal_id + '/pre_event_parks'
            ),
        };
    },
    computed: {
        deed_poll_url: function () {
            let vm = this;
            if (vm.global_settings) {
                for (var i = 0; i < vm.global_settings.length; i++) {
                    if (vm.global_settings[i].key == 'deed_poll_event') {
                        return vm.global_settings[i].value;
                    }
                }
            }
            return '';
        },
        credit_facility_link: function () {
            let vm = this;
            if (vm.global_settings) {
                for (var i = 0; i < vm.global_settings.length; i++) {
                    if (vm.global_settings[i].key == 'credit_facility_link') {
                        return vm.global_settings[i].value;
                    }
                }
            }
            return '';
        },
        fees_and_charges: function () {
            let vm = this;
            if (vm.global_settings) {
                for (var i = 0; i < vm.global_settings.length; i++) {
                    if (vm.global_settings[i].key == 'event_fees_and_charges') {
                        return vm.global_settings[i].value;
                    }
                }
            }
            return '';
        },
    },
    watch: {
        accreditation_type: function () {
            // eslint-disable-next-line vue/no-mutating-props
            this.proposal.event_other_details.accreditation_type =
                this.accreditation_type.key;
        },
    },
    mounted: function () {
        let vm = this;
        vm.fetchGlobalSettings();
        this.$nextTick(() => {
            vm.eventListeners();
        });
    },
    methods: {
        handleRadioChange: function (e) {
            if (e.target.value == 'true') {
                console.log(e.target.value);
                $('#show_docket').removeClass('hidden');
            } else {
                $('#show_docket').addClass('hidden');
            }
        },
        handleSelectionChange: function (e) {
            if (e.target.value == 'true') {
                console.log(e.target.value);
                $('#show_credit_link').removeClass('hidden');
            } else {
                $('#show_credit_link').addClass('hidden');
            }
        },
        showDockteNumber: function () {
            let vm = this;
            if (
                vm.proposal &&
                vm.proposal.event_other_details.credit_docket_books
            ) {
                var input = this.$refs.docket_books_yes;
                var e = document.createEvent('HTMLEvents');
                e.initEvent('change', true, true);
                var disabledStatus = input.disabled;
                try {
                    /* Firefox will not fire events for disabled widgets, so (temporarily) enabling them */
                    if (disabledStatus) {
                        input.disabled = false;
                    }
                    input.dispatchEvent(e);
                } finally {
                    if (disabledStatus) {
                        input.disabled = true;
                    }
                }
            }
        },
        showCreditFacilityLink: function () {
            let vm = this;
            if (vm.proposal && vm.proposal.event_other_details.credit_fees) {
                var input = this.$refs.credit_fees_yes;
                var e = document.createEvent('HTMLEvents');
                e.initEvent('change', true, true);
                var disabledStatus = input.disabled;
                try {
                    /* Firefox will not fire events for disabled widgets, so (temporarily) enabling them */
                    if (disabledStatus) {
                        input.disabled = false;
                    }
                    input.dispatchEvent(e);
                } finally {
                    if (disabledStatus) {
                        input.disabled = true;
                    }
                }
            }
        },
        addMooring: function () {
            let vm = this;
            var new_mooring = helpers.copyObject(
                vm.proposal.event_other_details.mooring
            );
            new_mooring.push('');
            vm.proposal.event_other_details.mooring = new_mooring;
            console.log(vm.proposal.event_other_details.mooring);
        },
        fetchAccreditationChoices: function () {
            let vm = this;
            vm.$http.get('/api/accreditation_choices.json').then(
                (response) => {
                    vm.accreditation_choices = response.body;
                    if (vm.proposal.event_other_details.accreditation_type) {
                        for (
                            var i = 0;
                            i < vm.accreditation_choices.length;
                            i++
                        ) {
                            if (
                                vm.accreditation_choices[i].key ==
                                vm.proposal.event_other_details
                                    .accreditation_type
                            ) {
                                vm.accreditation_type =
                                    vm.accreditation_choices[i];
                            }
                        }
                    }
                },
                (error) => {
                    console.log(error);
                }
            );
        },
        fetchLicencePeriodChoices: function () {
            let vm = this;
            vm.$http.get('/api/licence_period_choices.json').then(
                (response) => {
                    vm.licence_period_choices = response.body;
                },
                (error) => {
                    console.log(error);
                }
            );
        },
        fetchGlobalSettings: function () {
            let vm = this;
            vm.$http.get('/api/global_settings.json').then(
                (response) => {
                    vm.global_settings = response.body;
                },
                (error) => {
                    console.log(error);
                }
            );
        },
        checkProposalAccreditation: function () {
            let vm = this;
            if (vm.proposal && vm.proposal.event_other_details) {
                for (
                    var i = 0;
                    i < vm.proposal.event_other_details.accreditations.length;
                    i++
                ) {
                    vm.proposal.event_other_details.accreditations[
                        i
                    ].is_deleted = false;
                    vm.selected_accreditations.push(
                        vm.proposal.event_other_details.accreditations[i]
                            .accreditation_type
                    );
                }
            }
        },
        selectAccreditation: function (e, accreditation_type) {
            let vm = this;
            if (e.target.checked) {
                var found = false;
                for (
                    let i = 0;
                    i < vm.proposal.event_other_details.accreditations.length;
                    i++
                ) {
                    if (
                        vm.proposal.event_other_details.accreditations[i]
                            .accreditation_type == accreditation_type.key
                    ) {
                        found = true;
                        vm.proposal.event_other_details.accreditations[
                            i
                        ].is_deleted = false;
                    }
                }
                if (found == false) {
                    var data = {
                        accreditation_type: accreditation_type.key,
                        accreditation_expiry: null,
                        comments: '',
                        proposal_other_details:
                            vm.proposal.event_other_details.id,
                        is_deleted: false,
                        accreditation_type_value: accreditation_type.value,
                    };
                    const acc = helpers.copyObject(
                        vm.proposal.event_other_details.accreditations
                    );
                    acc.push(data);
                    vm.proposal.event_other_details.accreditations = acc;
                }
            } else {
                for (
                    let i = 0;
                    i < vm.proposal.event_other_details.accreditations.length;
                    i++
                ) {
                    if (
                        vm.proposal.event_other_details.accreditations[i]
                            .accreditation_type == accreditation_type.key
                    ) {
                        if (
                            vm.proposal.event_other_details.accreditations[i].id
                        ) {
                            const acc = helpers.copyObject(
                                vm.proposal.event_other_details.accreditations
                            );
                            acc[i].is_deleted = true;
                            vm.proposal.event_other_details.accreditations =
                                acc;
                        } else {
                            const acc = helpers.copyObject(
                                vm.proposal.event_other_details.accreditations
                            );
                            acc.splice(i, 1);
                            vm.proposal.event_other_details.accreditations =
                                acc;
                        }
                    }
                }
            }
        },
        eventListeners: function () {
            let vm = this;

            var date = new Date();
            var today = new Date(
                date.getFullYear(),
                date.getMonth(),
                date.getDate()
            );

            //Insurance expiry date listener
            $(vm.$refs.insurance_expiry).datetimepicker(vm.datepickerOptions);
            //Set minimum date on datetimepicker so that
            //insurance expiry date cannot be selected prior to today
            $(vm.$refs.insurance_expiry).data('DateTimePicker').minDate(today);
            $(vm.$refs.insurance_expiry).on('dp.change', function (e) {
                if (
                    $(vm.$refs.insurance_expiry).data('DateTimePicker').date()
                ) {
                    vm.proposal.event_other_details.insurance_expiry =
                        e.date.format('DD/MM/YYYY');
                } else if ($(vm.$refs.insurance_expiry).data('date') === '') {
                    vm.proposal.event_other_details.insurance_expiry = '';
                }
            });

            //Training date listener
            $(vm.$refs.training_date).datetimepicker(vm.datepickerOptions);
            //Set minimum date on datetimepicker so that
            //Training date cannot be selected prior to today
            $(vm.$refs.training_date).data('DateTimePicker').minDate(today);
            $(vm.$refs.training_date).on('dp.change', function (e) {
                if ($(vm.$refs.training_date).data('DateTimePicker').date()) {
                    vm.proposal.event_other_details.training_date =
                        e.date.format('DD/MM/YYYY');
                } else if ($(vm.$refs.training_date).data('date') === '') {
                    vm.proposal.event_other_details.training_date = '';
                }
            });
        },
    },
};
</script>

<style lang="css" scoped>
.borderDecoration {
    border: 1px solid;
    border-radius: 5px;
    padding: 5px;
    margin-top: 5px;
}
fieldset.scheduler-border {
    border: 1px groove #ddd !important;
    padding: 0 1.4em 1.4em 1.4em !important;
    margin: 0 0 1.5em 0 !important;
    -webkit-box-shadow: 0px 0px 0px 0px #000;
    box-shadow: 0px 0px 0px 0px #000;
}
legend.scheduler-border {
    width: inherit; /* Or auto */
    padding: 0 10px; /* To give a bit of padding on the left and right */
    border-bottom: none;
}
</style>
