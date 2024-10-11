<template>
    <div id="internalDash" class="container">
        <ComplianceDashTable level="internal" :url="compliances_url" />
    </div>
</template>
<script>
import ComplianceDashTable from '@common-utils/compliances_dashboard.vue';
import { api_endpoints } from '@/utils/hooks';
export default {
    name: 'InternalCompliancesDashboard',
    components: {
        ComplianceDashTable,
    },
    data() {
        return {
            compliances_url: api_endpoints.compliances_paginated_external,
        };
    },
    computed: {},
    watch: {},
    mounted: function () {},
    methods: {},
};
</script>
