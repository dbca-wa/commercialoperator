<template id="district_proposal_table">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <FormSection
                    :form-collapse="false"
                    label="District Applications"
                    index="district_applications"
                    subtitle=""
                >
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
                </FormSection>
            </div>
        </div>
    </div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue';
import FormSection from '@/components/forms/section_toggle.vue';

export default {
    name: 'FilmingDistrictProposalTableDash',
    components: {
        datatable,
        FormSection,
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
                dom: '<"container-fluid"<"row"<"col"l><"col"f><"col"<"float-end"B>>>>rtip', // 'lfBrtip'
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
