<template lang="html">
    <div id="editVessel">
        <modal
            transition="modal fade"
            :title="title"
            large
            @ok="ok()"
            @cancel="cancel()"
        >
            <div class="container-fluid">
                <div class="row">
                    <form
                        id="vessel-form"
                        class="form-horizontal"
                        name="vesselForm"
                    >
                        <alert v-if="showError" type="danger"
                            ><strong>{{ errorString }}</strong></alert
                        >
                        <div class="col-sm-12">
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Nominated Vessel</label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <input
                                            ref="capacity"
                                            v-model="vessel.nominated_vessel"
                                            class="form-control"
                                            name="capacity"
                                            type="text"
                                            required
                                        />
                                    </div>
                                </div>
                            </div>

                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >UVI No. / Reg. No.</label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <input
                                            ref="spv_no"
                                            v-model="vessel.spv_no"
                                            class="form-control"
                                            name="spv_no"
                                            type="text"
                                            required
                                        />
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Vessel length (m)</label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <input
                                            ref="vessel_length"
                                            v-model="vessel.vessel_length"
                                            class="form-control"
                                            name="vessel_length"
                                            type="text"
                                        />
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Vessel weight</label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <input
                                            ref="vessel_weight"
                                            v-model="vessel.vessel_weight"
                                            class="form-control"
                                            name="vessel_weight"
                                            type="text"
                                        />
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Number of tenders</label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <input
                                            ref="number_of_tenders"
                                            v-model.number="vessel.number_of_tenders"
                                            class="form-control"
                                            name="number_of_tenders"
                                            type="number"
                                        />
                                    </div>
                                </div>
                            </div>

                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Certificate of survey</label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <div
                                            v-if="vessel.certificate_of_survey"
                                            class="mb-2"
                                        >
                                            <a
                                                :href="vessel.certificate_of_survey"
                                                target="_blank"
                                                rel="noopener"
                                                >{{ certificateFilename }}</a
                                            >
                                            <button
                                                type="button"
                                                class="btn btn-link text-danger"
                                                @click="removeCertificate"
                                                title="Delete document"
                                                aria-label="Delete document"
                                            >
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </div>
                                        <span class="btn btn-link btn-file">
                                            <u>Attach Document</u>
                                            <input
                                                ref="certificate_of_survey"
                                                class="form-control"
                                                name="certificate_of_survey"
                                                type="file"
                                                @change="
                                                    handleCertificateChange
                                                "
                                            />
                                        </span>
                                        <div
                                            v-if="certificate_of_survey_filename"
                                            class="mt-2"
                                        >
                                            {{ certificate_of_survey_filename }}
                                            <button
                                                type="button"
                                                class="btn btn-link text-danger"
                                                @click="removeSelectedCertificate"
                                                title="Delete selected document"
                                                aria-label="Delete selected document"
                                            >
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            <template #footer>
                <button
                    v-if="issuingVessel"
                    type="button"
                    disabled
                    class="btn btn-primary"
                    @click="ok"
                >
                    <i class="fas fa-spinner fa-spin"></i> Processing
                </button>
                <button
                    v-else
                    type="button"
                    class="btn btn-primary"
                    @click="ok"
                >
                    Ok
                </button>
                <button type="button" class="btn btn-secondary" @click="cancel">
                    Cancel
                </button>
            </template>
        </modal>
    </div>
</template>

<script>
import modal from '@vue-utils/bootstrap-modal.vue';
import alert from '@vue-utils/alert.vue';
import { helpers, api_endpoints } from '@/utils/hooks.js';
export default {
    // eslint-disable-next-line vue/component-definition-name-casing
    name: 'Edit-Vessel',
    components: {
        modal,
        alert,
    },
    props: {
        // eslint-disable-next-line vue/prop-name-casing
        vessel_action: {
            type: String,
            default: 'edit',
        },
    },
    data: function () {
        return {
            isModalOpen: false,
            form: null,
            vessel: Object,
            certificate_of_survey_file: null,
            certificate_of_survey_filename: '',
            remove_certificate_of_survey: false,
            vessel_id: Number,
            access_types: null,
            vessel_access_id: null,
            state: 'proposed_vessel',
            issuingVessel: false,
            validation_form: null,
            hasErrors: false,
            errorString: '',
            successString: '',
            success: false,
            dateFormat: 'YYYY-MM-DD',
            localVesselAction: JSON.parse(JSON.stringify(this.vessel_action)),
        };
    },
    computed: {
        showError: function () {
            var vm = this;
            return vm.hasErrors;
        },
        title: function () {
            return this.localVesselAction == 'add'
                ? 'Add a new Vessel record'
                : 'Edit a vessel record';
        },
        certificateFilename: function () {
            const filename = this.vessel.certificate_of_survey
                .split('/')
                .pop();
            return decodeURIComponent(filename || 'Certificate of survey');
        },
    },
    watch: {
        vessel_action: {
            handler(newVal) {
                this.localVesselAction = JSON.parse(JSON.stringify(newVal));
            },
            deep: true,
        },
    },
    mounted: function () {
        let vm = this;

        vm.form = document.forms.vesselForm;
        this.$nextTick(() => {
            vm.eventListeners();
        });
    },
    methods: {
        ok: function () {
            let vm = this;
            // Check form validity
            if (helpers.validateForm(vm.form)) {
                console.log('Form is valid');
                vm.sendData();
            } else {
                console.warn('Form is not valid');
            }
        },
        cancel: function () {
            this.close();
        },
        close: function () {
            this.isModalOpen = false;
            this.vessel = {};
            this.certificate_of_survey_file = null;
            this.certificate_of_survey_filename = '';
            this.remove_certificate_of_survey = false;
            this.hasErrors = false;
        },
        fetchContact: function (id) {
            let vm = this;
            helpers.fetchUrl(api_endpoints.contact(id)).then(
                (response) => {
                    vm.contact = response;
                    vm.isModalOpen = true;
                },
                (error) => {
                    console.log(error);
                }
            );
        },
        fetchAccessTypes: function () {
            let vm = this;
            helpers.fetchUrl('/api/access_types.json').then(
                (res) => {
                    vm.access_types = res;
                },
                (err) => {
                    console.log(err);
                }
            );
        },
        fetchVessel: function (vid) {
            let vm = this;
            helpers
                .fetchUrl(helpers.add_endpoint_json(api_endpoints.vessels, vid))
                .then(
                    (res) => {
                        vm.vessel = res;
                        if (vm.vessel.access_type) {
                            vm.vessel_access_id = vm.vessel.access_type.id;
                        }
                        vm.vessel.vessel_length =
                            vm.vessel.vessel_length || vm.vessel.size || '';
                        vm.vessel.size = vm.vessel.size || vm.vessel.vessel_length || '';
                        vm.certificate_of_survey_file = null;
                        vm.certificate_of_survey_filename = '';
                        vm.remove_certificate_of_survey = false;
                    },
                    (err) => {
                        console.log(err);
                    }
                );
        },

        handleCertificateChange: function (event) {
            const selectedFile = event.target.files[0];
            this.certificate_of_survey_file = selectedFile || null;
            this.certificate_of_survey_filename = selectedFile
                ? selectedFile.name
                : '';
            this.remove_certificate_of_survey = false;
        },

        removeCertificate: function () {
            swal.fire({
                title: 'Remove document',
                text: 'Are you sure you want to remove this document?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Remove',
                confirmButtonColor: '#d9534f',
            }).then((result) => {
                if (!result.isConfirmed) {
                    return;
                }
                this.vessel.certificate_of_survey = null;
                this.certificate_of_survey_file = null;
                this.certificate_of_survey_filename = '';
                this.remove_certificate_of_survey = true;
            });
        },

        removeSelectedCertificate: function () {
            swal.fire({
                title: 'Remove document',
                text: 'Are you sure you want to remove this document?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Remove',
                confirmButtonColor: '#d9534f',
            }).then((result) => {
                if (!result.isConfirmed) {
                    return;
                }
                this.certificate_of_survey_file = null;
                this.certificate_of_survey_filename = '';
                this.$refs.certificate_of_survey.value = '';
            });
        },

        sendData: function () {
            let vm = this;
            vm.hasErrors = false;
            let vessel = JSON.parse(JSON.stringify(vm.vessel));
            vm.issuingVessel = true;
            let formData = new FormData();
            formData.append('nominated_vessel', vessel.nominated_vessel || '');
            formData.append('spv_no', vessel.spv_no || '');
            formData.append('size', vessel.vessel_length || vessel.size || '');
            formData.append('vessel_length', vessel.vessel_length || '');
            formData.append('vessel_weight', vessel.vessel_weight || '');
            formData.append(
                'proposal',
                (vessel.proposal && vessel.proposal.id) || vessel.proposal || ''
            );
            if (
                vessel.number_of_tenders !== null &&
                vessel.number_of_tenders !== ''
            ) {
                formData.append('number_of_tenders', vessel.number_of_tenders);
            }
            if (vm.certificate_of_survey_file) {
                formData.append(
                    'certificate_of_survey',
                    vm.certificate_of_survey_file
                );
            }
            if (vm.remove_certificate_of_survey && vm.vessel_id != null) {
                formData.append('certificate_of_survey_clear', 'true');
            }
            if (vm.localVesselAction == 'add' && vm.vessel_id == null) {
                helpers
                    .fetchUrl(api_endpoints.vessels, {
                        method: 'POST',
                        body: formData,
                    })
                    .then(
                        (response) => {
                            vm.issuingVessel = false;
                            vm.close();
                            swal.fire({
                                title: 'Created',
                                text: 'New vessel record has been created.',
                                icon: 'success',
                            });
                            vm.$emit('refreshFromResponse', response);
                        },
                        (error) => {
                            vm.hasErrors = true;
                            vm.issuingVessel = false;
                            vm.errorString = helpers.apiVueResourceError(error);
                        }
                    );
            } else {
                helpers
                    .fetchUrl(
                        helpers.add_endpoint_json(
                            api_endpoints.vessels,
                            vm.vessel_id + '/edit_vessel'
                        ),
                        {
                            method: 'POST',
                            body: formData,
                        }
                    )
                    .then(
                        (response) => {
                            vm.issuingVessel = false;
                            vm.close();
                            swal.fire({
                                title: 'Saved',
                                text: 'Vessel details has been saved.',
                                icon: 'success',
                            });
                            vm.$emit('refreshFromResponse', response);
                        },
                        (error) => {
                            vm.hasErrors = true;
                            vm.issuingVessel = false;
                            vm.errorString = helpers.apiVueResourceError(error);
                        }
                    );
            }
        },
        eventListeners: function () {},
    },
};
</script>

<style lang="css">
input[type='text'],
input[type='number'] {
    width: 40%;
    box-sizing: border-box;
    margin-bottom: 0.25rem;
}
</style>
