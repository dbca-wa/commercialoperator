<template id="vehicle_table">
    <div class="row">
        <div class="col-sm-12">
            <div class="row">
                <div v-if="!proposal.readonly" class="col-md-3">
                    <input
                        type="button"
                        style="margin-top: 25px"
                        class="btn btn-primary"
                        value="Add new vehicle"
                        @click.prevent="newVehicle"
                    />
                </div>
            </div>

            <div class="row">
                <div class="col-lg-12" style="margin-top: 25px">
                    <datatable
                        :id="datatable_id"
                        ref="vehicle_datatable"
                        :dt-options="vehicle_options"
                        :dt-headers="vehicle_headers"
                    />
                </div>
            </div>
        </div>
        <!-- Note: I'm removing :vehicle_id="vehicle_id" because it is not used in the component -->
        <editVehicle
            ref="edit_vehicle"
            :access_types="access_types"
            @refreshFromResponse="refreshFromResponse"
        ></editVehicle>
    </div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue';
import editVehicle from './edit_vehicle.vue';
import { api_endpoints } from '@/utils/hooks';
export default {
    name: 'VehicleTableDash',
    components: {
        datatable,
        editVehicle,
    },
    props: {
        proposal: {
            type: Object,
            required: true,
        },
        url: {
            type: String,
            required: true,
        },
        // eslint-disable-next-line vue/prop-name-casing
        access_types: {
            type: Array,
            required: true,
        },
    },
    data() {
        let vm = this;
        return {
            new_vehicle: {
                access_type: null,
                capacity: '',
                rego: '',
                rego_expiry: null,
                license: '',
                proposal: vm.proposal.id,
            },
            pBody: 'pBody' + vm._uid,
            datatable_id: 'vehicle-datatable-' + vm._uid,
            // Filters for Vehicles
            external_status: ['Due', 'Future', 'Under Review', 'Approved'],
            internal_status: ['Due', 'Future', 'With Assessor', 'Approved'],
            vehicle_headers: [
                'Vehicle Type',
                'Seating capacity',
                'Registration no.',
                'Registration Expiry',
                'Transport license no.',
                'Action',
            ],
            vehicle_options: {
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>",
                },
                responsive: true,
                ajax: {
                    url: vm.url,
                    dataSrc: '',
                },
                dom: 'lBfrtip',
                buttons: ['excel', 'csv'],
                columns: [
                    {
                        data: 'access_type',
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            return data.name;
                        },
                    },
                    {
                        data: 'capacity',
                    },
                    {
                        data: 'rego',
                    },
                    {
                        data: 'rego_expiry',
                    },
                    {
                        data: 'license',
                    },
                    {
                        data: '',
                        mRender: function (data, type, full) {
                            let links = '';
                            if (!vm.proposal.readonly) {
                                links += `<a href='#${full.id}' data-edit-vehicle='${full.id}'>Edit Vehicle</a><br/>`;
                                links += `<a href='#${full.id}' data-discard-vehicle='${full.id}'>Discard</a><br/>`;
                            }
                            return links;
                        },
                    },
                ],
                processing: true,
            },
        };
    },
    computed: {
        is_external: function () {
            return this.level == 'external';
        },
    },
    watch: {},
    mounted: function () {
        let vm = this;
        vm.fetchFilterLists();
        this.$nextTick(() => {
            vm.addEventListeners();
            vm.initialiseSearch();
        });
        if (vm.is_external) {
            var column = vm.$refs.vehicle_datatable.vmDataTable.columns(8); //Hide 'Assigned To column for external'
            column.visible(false);
        }
    },
    methods: {
        fetchFilterLists: function () {},
        newVehicle: function () {
            let vm = this;
            this.$refs.edit_vehicle.vehicle_id = null;
            var new_vehicle_another = {
                access_type: null,
                capacity: '',
                rego: '',
                rego_expiry: null,
                license: '',
                proposal: vm.proposal.id,
            };
            this.$refs.edit_vehicle.vehicle = new_vehicle_another;
            this.$refs.edit_vehicle.vehicle_action = 'add';
            this.$refs.edit_vehicle.isModalOpen = true;
        },
        editVehicle: function (id) {
            this.$refs.edit_vehicle.vehicle_id = id;
            this.$refs.edit_vehicle.fetchVehicle(id);
            this.$refs.edit_vehicle.isModalOpen = true;
        },
        discardVehicle: function (vehicle_id) {
            let vm = this;
            swal({
                title: 'Discard Vehicle',
                text: 'Are you sure you want to discard this vehicle?',
                type: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Discard Vehicle',
                confirmButtonColor: '#d9534f',
            }).then(
                () => {
                    vm.$http
                        .delete(api_endpoints.discard_vehicle(vehicle_id))
                        .then(
                            () => {
                                swal(
                                    'Discarded',
                                    'Your vehicle has been discarded',
                                    'success'
                                );
                                vm.$refs.vehicle_datatable.vmDataTable.ajax.reload();
                            },
                            (error) => {
                                console.log(error);
                            }
                        );
                },
                () => {}
            );
        },
        addEventListeners: function () {
            let vm = this;
            vm.$refs.vehicle_datatable.vmDataTable.on(
                'click',
                'a[data-edit-vehicle]',
                function (e) {
                    e.preventDefault();
                    var id = $(this).attr('data-edit-vehicle');
                    vm.editVehicle(id);
                }
            );
            // External Discard listener
            vm.$refs.vehicle_datatable.vmDataTable.on(
                'click',
                'a[data-discard-vehicle]',
                function (e) {
                    e.preventDefault();
                    var id = $(this).attr('data-discard-vehicle');
                    vm.discardVehicle(id);
                }
            );
        },
        refreshFromResponse: function () {
            this.$refs.vehicle_datatable.vmDataTable.ajax.reload();
        },
        initialiseSearch: function () {},
    },
};
</script>
<style scoped></style>
