<template lang="html">
    <div id="editVehicle">
        <modal
            transition="modal fade"
            :title="title"
            large
            @ok="ok()"
            @cancel="cancel()"
        >
            <div v-if="fetchingVehicle">
                <BootstrapSpinner
                    :center-of-screen="false"
                    class="text-primary"
                />
            </div>
            <div v-else-if="vehicle" class="container-fluid">
                <div class="row">
                    <form
                        ref="vehicleForm"
                        class="form-horizontal"
                        name="vehicleForm"
                    >
                        <alert v-if="showError" type="danger"
                            ><strong>{{ errorString }}</strong></alert
                        >
                        <div class="col-sm-12">
                            <div class="form-group">
                                <div class="row mb-3">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="access_type"
                                            >Vehicle Type</label
                                        >
                                    </div>
                                    <div
                                        id="access_type_parent"
                                        class="col-sm-9"
                                    >
                                        <select
                                            id="access_type"
                                            ref="access_type"
                                            v-model.number="
                                                accessTypeIdSelection
                                            "
                                            class="form-select"
                                            name="access_type"
                                            required
                                        >
                                            <option value="" :disabled="true">
                                                Select a Vehicle Type
                                            </option>
                                            <option
                                                v-for="a in access_types"
                                                :key="a.id"
                                                :value="a.id"
                                            >
                                                {{ a.name }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div class="form-group">
                                <div class="row mb-3">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Seating Capacity</label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <input
                                            ref="capacity"
                                            v-model="vehicle.capacity"
                                            class="form-control"
                                            name="capacity"
                                            type="number"
                                            required
                                        />
                                    </div>
                                </div>
                            </div>

                            <div class="form-group">
                                <div class="row mb-3">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Registration No.</label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <input
                                            ref="rego"
                                            v-model="vehicle.rego"
                                            class="form-control"
                                            name="rego"
                                            type="text"
                                            required
                                        />
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row mb-3">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Registration Expiry</label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <div
                                            ref="rego_expiry"
                                            class="input-group date"
                                            style="width: 40%"
                                        >
                                            <input
                                                v-model="vehicle.rego_expiry"
                                                type="date"
                                                class="form-control"
                                                name="rego_expiry"
                                                max="2999-12-31"
                                                placeholder="DD/MM/YYYY"
                                                required
                                            />
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
                    v-if="issuingVehicle"
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
import BootstrapSpinner from '../vue2-components/BootstrapSpinner.vue';

export default {
    // eslint-disable-next-line vue/component-definition-name-casing
    name: 'Edit-Vehicle',
    components: {
        modal,
        alert,
        BootstrapSpinner,
    },
    props: {
        proposal_id: {
            type: Number,
            default: null,
        },
        // eslint-disable-next-line vue/prop-name-casing
        vehicle_action: {
            type: String,
            default: 'edit',
        },
        // eslint-disable-next-line vue/prop-name-casing
        access_types: {
            type: Array,
            required: true,
        },
    },
    data: function () {
        return {
            isModalOpen: false,
            form: null,
            vehicle: this.defaultVehicle(),
            state: 'proposed_vehicle',
            fetchingVehicle: false,
            issuingVehicle: false,
            validation_form: null,
            hasErrors: false,
            errorString: '',
            successString: '',
            success: false,
            dateFormat: 'YYYY-MM-DD',
            localVehicleAction: JSON.parse(JSON.stringify(this.vehicle_action)),
        };
    },
    computed: {
        showError: function () {
            var vm = this;
            return vm.hasErrors;
        },
        title: function () {
            return this.localVehicleAction == 'add'
                ? 'Add a new Vehicle record'
                : 'Edit a vehicle record';
        },
        accessTypeIdSelection: {
            get() {
                return this.vehicle.access_type.id === null
                    ? ''
                    : this.vehicle.access_type.id;
            },
            set(newValue) {
                this.vehicle.access_type.id = newValue === '' ? null : newValue;
            },
        },
    },
    watch: {
        vehicle_action: {
            handler(newVal) {
                this.localVehicleAction = JSON.parse(JSON.stringify(newVal));
            },
            deep: true,
        },
        isModalOpen: {
            handler(newVal) {
                if (newVal && this.$refs.access_type) {
                    this.$nextTick(() => {
                        this.$refs.access_type?.focus();
                    });
                }
            },
        },
    },
    methods: {
        defaultVehicle: function () {
            return {
                capacity: null,
                rego: '',
                rego_expiry: '',
                // Provide the empty nested object so the template doesn't crash
                access_type: {
                    id: null,
                },
            };
        },
        ok: function () {
            let vm = this;
            // Use the template ref directly so it's always current
            let currentForm = vm.$refs.vehicleForm;

            if (currentForm && helpers.validateForm(currentForm)) {
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
            this.vehicle = this.defaultVehicle();
            this.hasErrors = false;
        },
        fetchVehicle: function (vid) {
            let vm = this;
            vm.fetchingVehicle = true;
            helpers
                .fetchUrl(
                    helpers.add_endpoint_json(api_endpoints.vehicles, vid)
                )
                .then(
                    (res) => {
                        vm.vehicle = res;
                    },
                    (err) => {
                        console.log(err);
                    }
                )
                .finally(() => {
                    vm.fetchingVehicle = false;
                    this.$nextTick(() => {
                        this.$refs.access_type.focus();
                    });
                });
        },
        sendData: function () {
            let vm = this;
            vm.hasErrors = false;
            let vehicle = JSON.parse(JSON.stringify(vm.vehicle));
            vehicle.proposal_id = vm.proposal_id;
            vehicle.proposal = vm.proposal_id;
            vehicle.access_type = vm.vehicle.access_type.id;
            vm.issuingVehicle = true;
            if (vm.localVehicleAction == 'add' && vm.vehicle.id == null) {
                helpers
                    .fetchUrl(api_endpoints.vehicles, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(vehicle),
                    })
                    .then(
                        (response) => {
                            vm.issuingVehicle = false;
                            vm.vehicle = vm.defaultVehicle();
                            vm.close();
                            swal.fire({
                                title: 'Created',
                                text: 'New vehicle record has been created.',
                                icon: 'success',
                            });
                            vm.$emit('refreshFromResponse', response);
                        },
                        (error) => {
                            vm.hasErrors = true;
                            vm.issuingVehicle = false;
                            vm.errorString = helpers.apiVueResourceError(error);
                        }
                    );
            } else {
                helpers
                    .fetchUrl(
                        helpers.add_endpoint_json(
                            api_endpoints.vehicles,
                            vm.vehicle.id + '/edit_vehicle'
                        ),
                        {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(vehicle),
                        }
                    )
                    .then(
                        (response) => {
                            vm.issuingVehicle = false;
                            vm.vehicle = {};
                            vm.close();
                            swal.fire({
                                title: 'Saved',
                                text: 'Vehicle details has been saved.',
                                icon: 'success',
                            });
                            vm.$emit('refreshFromResponse', response);
                        },
                        (error) => {
                            vm.hasErrors = true;
                            vm.issuingVehicle = false;
                            vm.errorString = helpers.apiVueResourceError(error);
                        }
                    );
            }
        },
    },
};
</script>
