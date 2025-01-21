<template lang="html">
    <div>
        <div class="form-group">
            <label :id="id" for="label" class="inline">{{ label }}</label>
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
                <HelpTextUrl :help_text_url="help_text_url" />
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
            <textarea
                v-model="localValue"
                :readonly="readonly"
                class="form-control"
                rows="5"
                :name="name"
                :required="isRequired"
            ></textarea>
            <!-- {{ value }}</textarea -->
            <br />
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
    components: { Comment, HelpText, HelpTextUrl },
    props: {
        name: {
            type: String,
            default: null,
        },
        value: {
            type: String,
            default: '',
        },
        id: {
            type: String,
            default: null,
        },
        isRequired: {
            type: Boolean,
            default: false,
        },
        // eslint-disable-next-line vue/prop-name-casing
        help_text: {
            type: String,
            default: null,
        },
        // eslint-disable-next-line vue/prop-name-casing
        help_text_assessor: {
            type: String,
            default: null,
        },
        assessorMode: {
            type: Boolean,
            default: false,
        },
        label: {
            type: String,
            default: null,
        },
        readonly: {
            type: Boolean,
            default: false,
        },
        // eslint-disable-next-line vue/prop-name-casing
        comment_value: {
            type: String,
            default: null,
        },
        // eslint-disable-next-line vue/prop-name-casing
        assessor_readonly: {
            type: Boolean,
            default: false,
        },
        // eslint-disable-next-line vue/prop-name-casing
        help_text_url: {
            type: String,
            default: null,
        },
        // eslint-disable-next-line vue/prop-name-casing
        help_text_assessor_url: {
            type: String,
            default: null,
        },
    },
    data() {
        return {
            showingComment: false,
            localValue: JSON.parse(JSON.stringify(this.value)),
        };
    },
    watch: {
        value: {
            handler: function (value) {
                this.localValue = value;
            },
            deep: true,
        },
    },
    methods: {
        toggleComment() {
            this.showingComment = !this.showingComment;
        },
        /**
         * Checks if the comments text field is not empty if the field is required to check for validity
         */
        isValid() {
            if (!this.isRequired) {
                return true;
            }
            const isValid =
                this.isRequired &&
                [null, undefined, ''].includes(this.localValue) === false;
            console.log(`Text-area is ${isValid ? 'valid' : 'not valid'}`);
            return isValid;
        },
    },
};
</script>

<style lang="css">
input {
    box-shadow: none;
}
</style>
