<template>
    <div id="internalDash" class="container">
        <ApprovalDashTable level="internal" :url="approvals_url" />
    </div>
</template>
<script>
import ApprovalDashTable from '@common-utils/approvals_dashboard.vue';
import { api_endpoints } from '@/utils/hooks';
export default {
    name: 'InternalApprovalDashboard',
    components: {
        ApprovalDashTable,
    },
    data() {
        return {
            //approvals_url: api_endpoints.approvals,
            approvals_url: api_endpoints.approvals_paginated_external,
        };
    },
    computed: {},
    watch: {},
    mounted: function () {},
    methods: {},
};
</script>
