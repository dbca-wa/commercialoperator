<!-- eslint-disable vue/no-mutating-props -->
<template lang="html">
    <div id="otherInfo" class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">
                        Safety<small></small>
                        <a
                            class="panelClicker"
                            :href="'#' + lBody"
                            data-toggle="collapse"
                            data-parent="#otherInfo"
                            expanded="true"
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
                            <div class="form-group">
                                <div class="row" style="margin-bottom: 5px">
                                    <div class="col-sm-6">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >What steps have been taken to
                                            ensure the safety of your filming
                                            party?
                                            <small>
                                                (Provide details of your safety
                                                and communication equipment
                                                and/or attach a copy of your
                                                safety and risk management
                                                plan)</small
                                            >
                                        </label>
                                    </div>
                                    <div class="col-sm-6">
                                        <div
                                            ref="safety_details"
                                            class="input-group date"
                                            style="width: 70%"
                                        >
                                            <textarea
                                                v-model="
                                                    proposal
                                                        .filming_other_details
                                                        .safety_details
                                                "
                                                type="text"
                                                class="form-control"
                                                name="safety_details"
                                                :disabled="
                                                    proposal.readonly ||
                                                    proposal.pending_amendment_request ||
                                                    proposal.is_amendment_proposal
                                                "
                                            ></textarea>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-sm-12">
                                        <FileField
                                            :id="'proposal' + proposal.id"
                                            :proposal_id="proposal.id"
                                            :is-repeatable="true"
                                            name="filming_safety_details"
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
                        Other <small></small>
                        <a
                            class="panelClicker"
                            :href="'#' + oBody"
                            data-toggle="collapse"
                            data-parent="#userInfo"
                            expanded="true"
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
                        <div class="form-horizontal col-sm-12 borderDecoration">
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
                                                proposal.filming_other_details
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
                                            name="filming_other_details"
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
                            expanded="true"
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
                        <div class="form-horizontal col-sm-12 borderDecoration">
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <label
                                            >Depending on the filming operation,
                                            fees and charges may apply. Please
                                            see commercial filming
                                            <a
                                                :href="fees_and_charges"
                                                target="_blank"
                                                >website</a
                                            >
                                            for information on fees and
                                            charges.</label
                                        >
                                    </div>
                                </div>
                                <div class="row">&nbsp;</div>
                                <div
                                    v-if="
                                        proposal.filming_other_details
                                            .camping_fee_waived
                                    "
                                    class="row"
                                >
                                    <div class="col-sm-6">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >For how many people
                                        </label>
                                    </div>
                                    <div
                                        class="col-sm-6"
                                        style="margin-bottom: 5px"
                                    >
                                        <div
                                            class="col-sm-6"
                                            style="margin-bottom: 5px"
                                        >
                                            <input
                                                v-model="
                                                    proposal
                                                        .filming_other_details
                                                        .fee_waived_num_people
                                                "
                                                type="text"
                                                class="form-control"
                                                name="num_cameras"
                                                placeholder=""
                                                :disabled="proposal.readonly"
                                            />
                                        </div>
                                    </div>
                                </div>
                                <div
                                    v-if="
                                        proposal.filming_other_details
                                            .camping_fee_waived
                                    "
                                    class="row"
                                >
                                    <div class="col-sm-12">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Make sure that you have a copy of
                                            the licence or lawful authority if
                                            issued. Camping gess may still
                                            apply.</label
                                        >
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
                        Insurance <small></small>
                        <a
                            class="panelClicker"
                            :href="'#' + iBody"
                            data-toggle="collapse"
                            data-parent="#userInfo"
                            expanded="true"
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
                        <div class="form-horizontal col-sm-12 borderDecoration">
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
                                                    filming authority, and in
                                                    the name of the applicant to
                                                    the extent of its rights and
                                                    interests, for a sum of not
                                                    less than AU$10 million per
                                                    event.
                                                </li>
                                                <li>
                                                    It is a requirement of all
                                                    filming authority holders to
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
                                                    proposal
                                                        .filming_other_details
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
                            expanded="true"
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
                        <div class="form-horizontal col-sm-12 borderDecoration">
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <label
                                            >It is a requirement of all filming
                                            authority holders to sign a deed
                                            poll to release and indemnify the
                                            State of Western Australia. Please
                                            note: electronic or digital
                                            signatures cannot be
                                            accepted.</label
                                        >
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
import FileField from '@/components/forms/filefield.vue';
export default {
    components: {
        FileField,
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
            global_settings: [],
            datepickerOptions: {
                format: 'DD/MM/YYYY',
                showClear: true,
                useCurrent: false,
                keepInvalid: true,
                allowInputToggle: true,
            },
        };
    },
    computed: {
        deed_poll_url: function () {
            let vm = this;
            if (vm.global_settings) {
                for (var i = 0; i < vm.global_settings.length; i++) {
                    if (vm.global_settings[i].key == 'deed_poll_filming') {
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
                    if (vm.global_settings[i].key == 'fees_and_charges') {
                        return vm.global_settings[i].value;
                    }
                }
            }
            return '';
        },
    },
    watch: {},
    mounted: function () {
        let vm = this;
        vm.fetchGlobalSettings();
        this.$nextTick(() => {
            vm.eventListeners();
        });
    },
    methods: {
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
                    vm.proposal.filming_other_details.insurance_expiry =
                        e.date.format('DD/MM/YYYY');
                } else if ($(vm.$refs.insurance_expiry).data('date') === '') {
                    vm.proposal.filming_other_details.insurance_expiry = '';
                }
            });
        },
    },
};
</script>

<style lang="css" scoped>
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
