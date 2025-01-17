<template id="park_table">
    <div class="row">
        <div class="col-sm-12">
            <div class="row">
                <div v-if="canEditActivities" class="col-md-3">
                    <input
                        type="button"
                        style="margin-top: 25px"
                        class="btn btn-primary"
                        value="Add"
                        @click.prevent="newPark"
                    />
                </div>
            </div>

            <div class="row">
                <div class="col-lg-12" style="margin-top: 25px">
                    <datatable
                        :id="datatable_id"
                        ref="park_datatable"
                        :dt-options="park_options"
                        :dt-headers="park_headers"
                    />
                </div>
            </div>
        </div>
        <!-- Note: I removed the :park_id="park_id", because it does not exist on this component  -->
        <editPark
            ref="edit_park"
            :district_proposal="district_proposal"
            :is_external="is_external"
            :can-edit-activities="canEditActivities"
            @refreshFromResponse="refreshFromResponse"
        ></editPark>
    </div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue';
import editPark from './edit_park.vue';
import { api_endpoints } from '@/utils/hooks';
export default {
    name: 'ParkTableDash',
    components: {
        datatable,
        editPark,
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
        hasDistrictAssessorMode: {
            type: Boolean,
            default: false,
        },
        // eslint-disable-next-line vue/prop-name-casing
        district_proposal: {
            type: Object,
            default: null,
        },
        canEditActivities: {
            type: Boolean,
            default: true,
        },
        // eslint-disable-next-line vue/prop-name-casing
        is_external: {
            type: Boolean,
            default: false,
        },
    },
    data() {
        let vm = this;
        return {
            new_park: {
                park: null,
                feature_of_interest: '',
                from_date: null,
                to_date: null,
                proposal: vm.proposal.id,
            },
            pBody: 'pBody' + vm._uid,
            datatable_id: 'park-datatable-' + vm._uid,
            // Filters for Parks
            park_headers: [
                'Park or Reserve',
                'Feature or site of Interest',
                'From',
                'To',
                'Itinerary/ Maps',
                'Action',
            ],
            park_options: {
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>",
                },
                responsive: true,
                ajax: {
                    url: vm.url,
                    dataSrc: '',
                },
                dom: '<"container-fluid"<"row"<"col"l><"col"f><"col"<"float-end"B>>>>rtip', // 'lfBrtip'
                buttons: ['excel', 'csv'],
                columns: [
                    {
                        data: 'park',
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            return data.name;
                        },
                    },
                    {
                        data: 'feature_of_interest',
                    },
                    {
                        data: 'from_date',
                    },
                    {
                        data: 'to_date',
                    },
                    {
                        data: 'filming_park_documents',
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            let links = '';
                            _.forEach(data, function (item) {
                                links += `<a href='${item._file}' target='_blank' style='padding-left: 52px;'>${item.name}</a><br/>`;
                            });
                            return links;
                        },
                    },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            let links = '';
                            if (vm.is_external) {
                                if (
                                    !vm.proposal.readonly &&
                                    full.park.visible_to_external
                                ) {
                                    links += `<a href='#${full.id}' data-edit-park='${full.id}'>Edit Park</a><br/>`;
                                    links += `<a href='#${full.id}' data-discard-park='${full.id}'>Discard</a><br/>`;
                                }
                            }
                            if (!vm.is_external) {
                                if (full.can_assessor_edit) {
                                    links += `<a href='#${full.id}' data-edit-park='${full.id}'>Edit Park</a><br/>`;
                                    links += `<a href='#${full.id}' data-discard-park='${full.id}'>Discard</a><br/>`;
                                }
                            }
                            return links;
                        },
                    },
                ],
                processing: true,
            },
        };
    },
    computed: {},
    watch: {},
    mounted: function () {
        let vm = this;
        vm.fetchFilterLists();
        this.$nextTick(() => {
            vm.addEventListeners();
            vm.initialiseSearch();
        });
    },
    methods: {
        fetchFilterLists: function () {},
        newPark: function () {
            let vm = this;
            this.$refs.edit_park.park_id = null;
            var new_park_another = {
                park: null,
                feature_of_interest: '',
                from_date: null,
                to_date: null,
                proposal: vm.proposal.id,
            };
            this.$refs.edit_park.park = new_park_another;
            this.$refs.edit_park.localParkAction = 'add';
            this.$refs.edit_park.isModalOpen = true;
        },
        editPark: function (id) {
            this.$refs.edit_park.park_id = id;
            this.$refs.edit_park.fetchPark(id);
            this.$refs.edit_park.isModalOpen = true;
        },
        discardPark: function (park_id) {
            let vm = this;
            swal.fire({
                title: 'Discard Park',
                text: 'Are you sure you want to discard this park?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Discard Park',
                confirmButtonColor: '#d9534f',
            }).then(
                (result) => {
                    if (!result.isConfirmed) {
                        return;
                    }
                    vm.$http
                        .delete(api_endpoints.discard_filming_park(park_id))
                        .then(
                            () => {
                                swal.fire({
                                    title: 'Discarded',
                                    text: 'Your park has been discarded',
                                    icon: 'success',
                                });
                                vm.$refs.park_datatable.vmDataTable.ajax.reload();
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
            vm.$refs.park_datatable.vmDataTable.on(
                'click',
                'a[data-edit-park]',
                function (e) {
                    e.preventDefault();
                    var id = $(this).attr('data-edit-park');
                    vm.editPark(id);
                }
            );
            // External Discard listener
            vm.$refs.park_datatable.vmDataTable.on(
                'click',
                'a[data-discard-park]',
                function (e) {
                    e.preventDefault();
                    var id = $(this).attr('data-discard-park');
                    vm.discardPark(id);
                }
            );
        },
        refreshFromResponse: function () {
            this.$refs.park_datatable.vmDataTable.ajax.reload();
        },
        initialiseSearch: function () {},
    },
};
</script>
<style scoped></style>
