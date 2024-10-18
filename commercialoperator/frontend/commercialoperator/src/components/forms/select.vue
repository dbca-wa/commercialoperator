<template lang="html">
    <div>
        <div class="form-group">
            <label :id="id">{{ label }}</label>

            <template v-if="help_text">
                <HelpText :help_text="help_text" />
            </template>
            <template v-if="help_text_assessor && assessorMode">
                <HelpText
                    :help_text="help_text_assessor"
                    assessor-mode="{assessorMode}"
                    is-for-assessor="{true}"
                />
            </template>

            <template v-if="help_text_url">
                <HelpText :help_text_url="help_text_url" />
            </template>
            <template v-if="help_text_assessor_url && assessorMode">
                <HelpTextUrl
                    :help_text_url="help_text_assessor_url"
                    assessor-mode="{assessorMode}"
                    is-for-assessor="{true}"
                />
            </template>

            <template v-if="assessorMode && !assessor_readonly">
                <template v-if="!showingComment">
                    <a
                        v-if="
                            comment_value != null &&
                            comment_value != undefined &&
                            comment_value != ''
                        "
                        href=""
                        @click.prevent="toggleComment"
                        ><i style="color: red" class="fa fa-comment-o"
                            >&nbsp;</i
                        ></a
                    >
                    <a v-else href="" @click.prevent="toggleComment"
                        ><i class="fa fa-comment-o">&nbsp;</i></a
                    >
                </template>
                <a v-else href="" @click.prevent="toggleComment"
                    ><i class="fa fa-ban">&nbsp;</i></a
                >
            </template>

            <template v-if="readonly">
                <select
                    v-if="!isMultiple"
                    :id="selectid"
                    ref="selectB"
                    disabled
                    :name="name"
                    class="form-control"
                    :data-conditions="cons"
                    style="width: 100%"
                >
                    <option value="">Select...</option>
                    <option
                        v-for="op in options"
                        :key="op.value"
                        :value="op.value"
                        :selected="op.value == value"
                        @change="handleChange"
                    >
                        {{ op.label }}
                    </option>
                </select>
                <select
                    v-else
                    :id="selectid"
                    ref="selectB"
                    disabled
                    class="form-control"
                    multiple
                    style="width: 100%"
                >
                    <option value="">Select...</option>
                    <option
                        v-for="op in options"
                        :key="op.value"
                        :value="op.value"
                        :selected="multipleSelection(op.value)"
                    >
                        {{ op.label }}
                    </option>
                </select>
                <template v-if="isMultiple">
                    <input
                        v-for="v in value"
                        :key="v"
                        input
                        type="hidden"
                        :name="name"
                        :value="v"
                        :required="isRequired"
                    />
                </template>
                <template v-else>
                    <input
                        type="hidden"
                        :name="name"
                        :value="value"
                        :required="isRequired"
                    />
                </template>
            </template>
            <template v-else>
                <select
                    v-if="!isMultiple"
                    :id="selectid"
                    ref="selectB"
                    :name="name"
                    class="form-control"
                    :data-conditions="cons"
                    style="width: 100%"
                    :required="isRequired"
                >
                    <option value="">Select...</option>
                    <option
                        v-for="op in options"
                        :key="op.value"
                        :value="op.value"
                        :selected="op.value == value"
                        @change="handleChange"
                    >
                        {{ op.label }}
                    </option>
                </select>
                <select
                    v-else
                    :id="selectid"
                    ref="selectB"
                    :name="name"
                    class="form-control"
                    multiple
                    style="width: 100%"
                    :required="isRequired"
                >
                    <option value="">Select...</option>
                    <option
                        v-for="op in options"
                        :key="op.value"
                        :value="op.value"
                        :selected="multipleSelection(op.value)"
                    >
                        {{ op.label }}
                    </option>
                </select>
            </template>
        </div>

        <Comment
            v-show="showingComment && assessorMode"
            :question="label"
            :readonly="assessor_readonly"
            :name="name + '-comment-field'"
            :value="comment_value"
        />
    </div>
</template>

<script>
import Comment from './comment.vue';
import HelpText from './help_text.vue';
import HelpTextUrl from './help_text_url.vue';
export default {
    name: 'SelectComponent',
    components: { Comment, HelpText, HelpTextUrl },
    props: {
        // eslint-disable-next-line vue/require-default-prop
        name: String,
        // eslint-disable-next-line vue/require-default-prop
        label: String,
        // eslint-disable-next-line vue/require-default-prop
        id: String,
        // eslint-disable-next-line vue/require-default-prop
        isRequired: String,
        // eslint-disable-next-line vue/prop-name-casing, vue/require-default-prop
        help_text: String,
        // eslint-disable-next-line vue/prop-name-casing, vue/require-default-prop
        help_text_assessor: String,
        // eslint-disable-next-line vue/prop-name-casing, vue/require-default-prop
        help_text_url: String,
        // eslint-disable-next-line vue/prop-name-casing, vue/require-default-prop
        help_text_assessor_url: String,
        // eslint-disable-next-line vue/require-default-prop
        value: [String, Array],
        // eslint-disable-next-line vue/prop-name-casing, vue/require-default-prop
        comment_value: String,
        // eslint-disable-next-line vue/prop-name-casing
        assessor_readonly: Boolean,
        // eslint-disable-next-line vue/require-default-prop
        options: Array,
        // eslint-disable-next-line vue/require-default-prop
        conditions: Object,
        // eslint-disable-next-line vue/require-default-prop
        handleChange: null,
        // eslint-disable-next-line vue/require-prop-types
        isMultiple: {
            default: function () {
                return false;
            },
        },
        // eslint-disable-next-line vue/require-prop-types
        assessorMode: {
            default: function () {
                return false;
            },
        },
        readonly: Boolean,
    },
    data: function () {
        let vm = this;
        return {
            selected: this.isMultiple ? [] : '',
            selectid: 'select' + vm._uid,
            multipleSelected: [],
            showingComment: false,
        };
    },
    computed: {
        cons: function () {
            return JSON.stringify(this.conditions);
        },
    },
    mounted: function () {
        this.init();
    },
    methods: {
        toggleComment() {
            this.showingComment = !this.showingComment;
        },

        multipleSelection: function (val) {
            if (Array.isArray(this.value)) {
                if (this.value.find((v) => v == val)) {
                    return true;
                }
            } else {
                if (this.value == val) {
                    return true;
                }
            }
            return false;
        },
        init: function () {
            let vm = this;
            setTimeout(function () {
                $('#' + vm.selectid)
                    .select2({
                        theme: 'bootstrap-5',
                        allowClear: true,
                        placeholder: 'Select...',
                    })
                    .on('select2:select', function (e) {
                        var selected = $(e.currentTarget);
                        vm.handleChange(selected[0]);
                        e.preventDefault();
                        if (vm.isMultiple) {
                            vm.multipleSelected = selected.val();
                        }
                    })
                    .on('select2:unselect', function (e) {
                        var selected = $(e.currentTarget);
                        vm.handleChange(selected[0]);
                        e.preventDefault();
                        if (vm.isMultiple) {
                            vm.multipleSelected = selected.val();
                        }
                    });
                if (vm.value) {
                    vm.handleChange(vm.$refs.selectB);
                }
            }, 100);
        },
    },
};
</script>

<style lang="css">
.select2-container {
    width: 100% !important;
}

input {
    box-shadow: none;
}
</style>
