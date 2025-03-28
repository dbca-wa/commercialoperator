<template lang="html">
    <div>
        <Treeselect
            ref="treeselect"
            v-model="localValue"
            :options="options"
            :open-on-click="true"
            :multiple="multiple"
            :max-height="max_height"
            :value-consists-of="value_consists_of"
            :clearable="clearable"
            :flat="flat"
            :default-expand-level="default_expand_level"
            :normalizer="normalizer"
            :open-direction="open_direction"
            :disabled="disabled"
            :open-on-focus="true"
            :limit="localLimit"
            :close-on-select="closeOnSelect"
            :disable-branch-nodes="disableBranchNodes"
            :z-index="zIndex"
        >
            <label
                slot="option-label"
                slot-scope="{ node, labelClassName }"
                :class="labelClassName"
            >
                <div class="row">
                    <div class="col-sm-8 text-nowrap">
                        {{ node.raw.name }}
                    </div>
                    <div
                        v-if="node.raw.can_edit"
                        class="col-sm-4 option-label-container"
                    >
                        <div class="text-nowrap pull-right">
                            <a
                                v-if="is_checked(node)"
                                @mousedown.stop="edit_activities($event, node)"
                                >{{ edit_display_text(node) }}
                                <i class="fa fa-edit"></i
                            ></a>
                            <a v-else style="color: grey">
                                {{ edit_display_text(node) }}
                                <i class="fa fa-edit"></i>
                            </a>
                        </div>
                    </div>
                </div>
            </label>

            <div slot="value-label" slot-scope="{ node }">
                <div v-if="allow_edit">
                    <a
                        :disabled="!is_checked(node)"
                        :title="edit_display_text(node)"
                        @mousedown.stop="edit_activities($event, node)"
                    >
                        {{ node.label }}
                    </a>
                </div>
                <div v-else>
                    <a> {{ node.label }} </a>
                </div>
            </div>
        </Treeselect>
    </div>
</template>

<script>
// import the component
import Treeselect from '@riophae/vue-treeselect';
// import the styles
import '@riophae/vue-treeselect/dist/vue-treeselect.css';

export default {
    name: 'TreeSelect',
    components: {
        Treeselect,
    },
    props: {
        proposal: {
            type: Object,
            required: true,
        },
        // eslint-disable-next-line vue/require-default-prop
        value: {
            type: Array,
            required: false,
        },
        // eslint-disable-next-line vue/require-default-prop
        options: {
            type: Array,
            required: false,
        },
        flat: {
            type: Boolean,
            default: false,
        },
        // eslint-disable-next-line vue/prop-name-casing
        always_open: {
            type: Boolean,
            default: true,
        },
        clearable: {
            type: Boolean,
            default: false,
        },
        multiple: {
            type: Boolean,
            default: true,
        },
        // eslint-disable-next-line vue/prop-name-casing
        max_height: {
            type: Number,
            default: 350,
        },
        // eslint-disable-next-line vue/prop-name-casing
        default_expand_level: {
            type: Number,
            default: 0,
        },
        // eslint-disable-next-line vue/prop-name-casing
        value_consists_of: {
            type: String,
            default: 'LEAF_PRIORITY', // last leaf nodes get pushed to selected_items array
        },
        // eslint-disable-next-line vue/prop-name-casing
        open_direction: {
            type: String,
            default: 'bottom',
        },
        // eslint-disable-next-line vue/prop-name-casing
        allow_edit: {
            type: Boolean,
            default: false,
        },
        disabled: {
            type: Boolean,
            default: false,
        },
        limit: {
            type: Number,
            default: Infinity,
        },
        closeOnSelect: {
            type: Boolean,
            default: false,
        },
        disableBranchNodes: {
            type: Boolean,
            default: false,
        },
        zIndex: {
            type: Number,
            default: 999,
        },
    },
    data() {
        return {
            normalizer(node) {
                return {
                    id: node.last_leaf ? node.id : node.name,
                    // eslint-disable-next-line no-prototype-builtins
                    label: node.hasOwnProperty('label')
                        ? node.label
                        : node.name,
                    children: node.children,
                    isDisabled: node.is_disabled,
                };
            },
            // Note: I changed from using the prop `value` (props should not be mutated) to using a `localValue` data property
            localValue: this.value,
            // Note: I changed from using the prop `limit` (props should not be mutated) to using a `localLimit` data property
            localLimit: this.limit,
        };
    },

    computed: {},
    watch: {
        localValue: function (newValue) {
            /* allows two-way update of array value ( 'selected_access' )
               Requires parent Prop: ' :value.sync="selected_access" ', eg.
               <TreeSelect ref="selected_access" :proposal="proposal" :value.sync="selected_access" :options="land_access_options" :default_expand_level="1"></TreeSelect>
            */
            console.info('new localValue:', newValue);

            this.$emit('update:value', newValue);
        },
    },

    updated: function () {},

    mounted: function () {
        if (!this.disabled) {
            this.localLimit = 20;
        }
    },

    methods: {
        get_node_id: function (node) {
            //id: node.last_leaf ? node.id : (node.hasOwnProperty('node_id') : node.node_id ? node.name), // this is a nested if statement
            if (node.last_leaf) {
                return node.id;
                // eslint-disable-next-line no-prototype-builtins
            } else if (node.hasOwnProperty('node_id')) {
                return node.node_id;
            } else {
                return node.name;
            }
        },
        edit_display_text: function (node) {
            // eslint-disable-next-line no-prototype-builtins
            if (node.raw.hasOwnProperty('sections')) {
                return 'Edit sections and activities';
            } else {
                return 'Edit access and activities';
            }
        },
        edit_activities: function (event, node) {
            event.stopPropagation();
            // eslint-disable-next-line no-prototype-builtins
            if (node.raw.hasOwnProperty('sections')) {
                this.$parent.$parent.edit_sections(node);
                // eslint-disable-next-line no-prototype-builtins
            } else if (node.raw.hasOwnProperty('allowed_zone_activities')) {
                this.$parent.$parent.edit_activities(node);
            } else {
                this.$parent.$parent.edit_activities(node);
            }
        },
        is_checked: function (node) {
            return this.value.includes(node.id);
        },
    },
};
</script>

<style lang="css" scoped>
.option-label-container {
    z-index: 999;
}
</style>

/* data() { return { normalizer(node) { return { id: node.name, label:
node.name, children: node.children, } }, /* _selected_items: [], _options: [],
selected_items: [3,5], options: [ { id: 1, label: 'a', children: [ { id: 2,
label: 'aa', can_edit: false, }, { id: 3, label: 'ab', can_edit: true, } ], }, {
id: 4, label: 'b', can_edit: false, }, { id: 5, label: 'c', can_edit: false, }
], */ } }, */
