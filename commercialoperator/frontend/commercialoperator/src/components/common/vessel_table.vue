<template id="vessel_table">
    <div class="row">
        <div class="col-sm-12">
            <div class="row">
                <div v-if="!proposal.readonly" class="col-md-3">
                    <input
                        type="button"
                        style="margin-top: 25px"
                        class="btn btn-primary"
                        value="Add new vessel"
                        @click.prevent="newVessel"
                    />
                </div>
            </div>

            <div class="row">
                <div class="col-lg-12" style="margin-top: 25px">
                    <datatable
                        :id="datatable_id"
                        ref="vessel_datatable"
                        :dt-options="vessel_options"
                        :dt-headers="vessel_headers"
                    />
                </div>
            </div>
        </div>
        <editVessel
            ref="edit_vessel"
            @refreshFromResponse="refreshFromResponse"
        ></editVessel>
    </div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue';
import editVessel from './edit_vessel.vue';
import { api_endpoints, constants, helpers } from '@/utils/hooks';
import { v4 as uuid } from 'uuid';
import $ from 'jquery'
export default {
    name: 'VesselTableDash',
    components: {
        datatable,
        editVessel,
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
    },
    data() {
        let vm = this;
        return {
            new_vessel: {
                nominated_vessel: '',
                spv_no: '',
                size: '',
                vessel_length: '',
                vessel_weight: '',
                number_of_tenders: null,
                certificate_of_survey: null,
                proposal: vm.proposal.id,
            },
            pBody: 'pBody' + uuid(),
            datatable_id: 'vessel-datatable-' + uuid(),
            // Filters for Vessels

            vessel_headers: [
                'Nominated Vessel',
                'UVI No. / Reg. No.',
                'Vessel length (m)',
                'Vessel weight',
                'Number of tenders',
                'Certificate of survey',
                'Action',
            ],
            vessel_options: {
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                columnDefs: [
                    { responsivePriority: 1, targets: 0 },
                    {
                        responsivePriority: 2,
                        targets: -1,
                    },
                ],
                responsive: true,
                ajax: {
                    url: vm.url,
                    dataSrc: '',
                },
                dom: constants.DATATABLE_DOM_HTML,
                buttons: [
                    {
                        extend: 'excelHtml5',
                        text: 'Excel',
                        className: 'btn btn-primary me-2 rounded',
                        exportOptions: {
                            orthogonal: 'export',
                        },
                    },
                    {
                        extend: 'csvHtml5',
                        text: 'CSV',
                        className: 'btn btn-primary rounded',
                        exportOptions: {
                            orthogonal: 'export',
                        },
                    },
                ],
                columns: [
                    {
                        data: 'nominated_vessel',
                        mRender: function (data, type, full) {
                            return full.nominated_vessel;
                        },
                    },
                    {
                        data: 'spv_no',
                    },
                    {
                        data: 'vessel_length',
                        mRender: function (data, type, full) {
                            return full.vessel_length || full.size || '';
                        },
                    },
                    {
                        data: 'vessel_weight',
                    },
                    {
                        data: 'number_of_tenders',
                    },
                    {
                        data: 'certificate_of_survey',
                        mRender: function (data, type, full) {
                            if (!full.certificate_of_survey) {
                                return '';
                            }
                            return `<a href='${full.certificate_of_survey}' target='_blank' rel='noopener'>View document</a>`;
                        },
                    },
                    {
                        data: 'id',
                        orderable: false,
                        searchable: false,
                        mRender: function (data, type, full) {
                            let links = '';
                            if (!vm.proposal.readonly) {
                                links += `<a href='#${full.id}' data-edit-vessel='${full.id}'>Edit Vessel</a><br/>`;
                                links += `<a href='#${full.id}' data-discard-vessel='${full.id}'>Discard</a><br/>`;
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
            var column = vm.$refs.vessel_datatable.vmDataTable.columns(8); //Hide 'Assigned To column for external'
            column.visible(false);
        }
    },
    methods: {
        fetchFilterLists: function () {},
        newVessel: function () {
            let vm = this;
            this.$refs.edit_vessel.vessel_id = null;
            this.$refs.edit_vessel.certificate_of_survey_file = null;
            this.$refs.edit_vessel.certificate_of_survey_filename = '';
            var new_vessel_another = {
                nominated_vessel: '',
                spv_no: '',
                size: '',
                vessel_length: '',
                vessel_weight: '',
                number_of_tenders: null,
                certificate_of_survey: null,
                proposal: vm.proposal.id,
            };
            this.$refs.edit_vessel.vessel = new_vessel_another;
            this.$refs.edit_vessel.localVesselAction = 'add';
            this.$refs.edit_vessel.isModalOpen = true;
        },
        editVessel: function (id) {
            this.$refs.edit_vessel.vessel_id = id;
            this.$refs.edit_vessel.fetchVessel(id);
            this.$refs.edit_vessel.isModalOpen = true;
        },
        discardVessel: function (vessel_id) {
            let vm = this;
            swal.fire({
                title: 'Discard Vessel',
                text: 'Are you sure you want to discard this vessel?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Discard Vessel',
                confirmButtonColor: '#d9534f',
            }).then(
                (result) => {
                    if (!result.isConfirmed) {
                        return;
                    }
                    helpers
                        .fetchUrl(api_endpoints.discard_vessel(vessel_id), {
                            method: 'DELETE',
                        })
                        .then(
                            () => {
                                swal.fire({
                                    title: 'Discarded',
                                    text: 'Your vessel has been discarded',
                                    icon: 'success',
                                });
                                vm.$refs.vessel_datatable.vmDataTable.ajax.reload();
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
            vm.$refs.vessel_datatable.vmDataTable.on(
                'click',
                'a[data-edit-vessel]',
                function (e) {
                    e.preventDefault();
                    var id = $(this).attr('data-edit-vessel');
                    vm.editVessel(id);
                }
            );
            // External Discard listener
            vm.$refs.vessel_datatable.vmDataTable.on(
                'click',
                'a[data-discard-vessel]',
                function (e) {
                    e.preventDefault();
                    var id = $(this).attr('data-discard-vessel');
                    vm.discardVessel(id);
                }
            );
        },
        refreshFromResponse: function () {
            this.$refs.vessel_datatable.vmDataTable.ajax.reload();
        },
        initialiseSearch: function () {},
    },
};
</script>
<style scoped></style>
