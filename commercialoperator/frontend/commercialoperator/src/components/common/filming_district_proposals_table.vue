<template id="district_proposal_table">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">
                        District Applications
                        <a
                            :href="'#' + pBody"
                            data-toggle="collapse"
                            data-parent="#userInfo"
                            expanded="true"
                            :aria-controls="pBody"
                        >
                            <span
                                class="glyphicon glyphicon-chevron-up pull-right"
                            ></span>
                        </a>
                    </h3>
                </div>

                <div :id="pBody" class="panel-body collapse in">
                    <div class="row">
                        <div class="col-lg-12" style="margin-top: 25px">
                            <datatable
                                :id="datatable_id"
                                ref="district_proposal_datatable"
                                :dt-options="district_proposal_options"
                                :dt-headers="district_proposal_headers"
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue';
export default {
    name: 'FilmingDistrictProposalTableDash',
    components: {
        datatable,
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
            pBody: 'pBody' + vm._uid,
            datatable_id: 'district-proposal-datatable-' + vm._uid,

            district_proposal_headers: [
                'District',
                'Status',
                'Assigned Officer',
                'Action',
            ],
            district_proposal_options: {
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
                        data: 'district_name',
                    },
                    {
                        data: 'processing_status',
                    },
                    {
                        data: 'assigned_officer',
                    },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            let links = '';

                            links += full.district_assessor_can_assess
                                ? `<a href='/internal/proposal/${full.proposal}/district_proposal/${full.id}'>Process</a><br/>`
                                : `<a href='/internal/proposal/${full.proposal}/district_proposal/${full.id}'>View</a><br/>`;

                            return links;
                        },
                        // name: ''
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
    },
    methods: {
        fetchFilterLists: function () {},
        addEventListeners: function () {},
        refreshFromResponse: function () {
            this.$refs.district_proposal_datatable.vmDataTable.ajax.reload();
        },
        initialiseSearch: function () {},
    },
};
</script>
<style scoped></style>
