<template>
    <div id="internalDash" class="container">
        <FormSection
            :form-collapse="false"
            label="Compliance with requirements"
            index="compliance_with_requirements"
        >
            <ComplianceDashTable level="internal" :url="compliances_url" />
        </FormSection>
    </div>
</template>
<script>
import FormSection from '@/components/forms/section_toggle.vue';
import ComplianceDashTable from '@common-utils/compliances_dashboard.vue';
import { api_endpoints } from '@/utils/hooks';
export default {
    name: 'InternalCompliancesDashboard',
    components: {
        FormSection,
        ComplianceDashTable,
    },
    data() {
        return {
            compliances_url: api_endpoints.compliances_paginated_internal,
        };
    },
    computed: {},
    watch: {},
    mounted: function () {},
    methods: {},
};
</script>
