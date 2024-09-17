<template lang="html">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">
                        Commercial Event Questionnaire<small></small>
                        <a
                            class="panelClicker"
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
                    <div
                        v-if="proposal.applicant_training_completed"
                        class="form-horizontal col-sm-12"
                    >
                        <div v-if="proposal.applicant_type == 'ORG'">
                            <label style="color: green"
                                >Your online training has already been completed
                                this year. Please proceed to pay and submit the
                                application.</label
                            >
                        </div>
                        <div v-else>
                            <label style="color: green"
                                >Your online training has been completed. Please
                                proceed to pay and submit the
                                application.</label
                            >
                        </div>
                    </div>
                    <div v-else>
                        <div class="form-horizontal col-sm-12 borderDecoration">
                            <div class="row">
                                <alert
                                    v-if="showError"
                                    type="danger"
                                    style="color: red"
                                    ><strong>{{ errorString }}</strong></alert
                                >
                            </div>
                            <label v-if="training_doc_url" class="control-label"
                                >Complete the questionnaire below. Information
                                to help you is
                                <a :href="training_doc_url" target="_blank"
                                    >here</a
                                >.</label
                            >
                            <label v-else class="control-label"
                                >Complete the questionnaire below. Information
                                to help you is here.</label
                            >
                            <div class="row">
                                <form>
                                    <ul
                                        v-for="q in questions"
                                        :key="q.id"
                                        class="list-unstyled col-sm-12"
                                    >
                                        <div class="row">
                                            <div class="col-sm-12">
                                                <li class="col-sm-6">
                                                    <label
                                                        class="control-label"
                                                        style="text-align: left"
                                                        >{{
                                                            q.question_text
                                                        }}</label
                                                    >
                                                </li>
                                                <ul
                                                    class="list-inline col-sm-6"
                                                >
                                                    <li
                                                        v-if="q.answer_one"
                                                        class="list-inline-item"
                                                    >
                                                        <input
                                                            :id="
                                                                answer_one +
                                                                q.id
                                                            "
                                                            ref="Checkbox"
                                                            v-model="q.selected"
                                                            class="form-check-input"
                                                            type="radio"
                                                            :name="
                                                                'option' + q.id
                                                            "
                                                            :value="answer_one"
                                                            data-parsley-required
                                                            :disabled="
                                                                proposal.readonly
                                                            "
                                                        />
                                                        {{ q.answer_one }}
                                                    </li>
                                                    <br />
                                                    <li
                                                        v-if="q.answer_two"
                                                        class="list-inline-item"
                                                    >
                                                        <input
                                                            :id="
                                                                answer_two +
                                                                q.id
                                                            "
                                                            ref="Checkbox"
                                                            v-model="q.selected"
                                                            class="form-check-input"
                                                            type="radio"
                                                            :name="
                                                                'option' + q.id
                                                            "
                                                            :value="answer_two"
                                                            data-parsley-required
                                                            :disabled="
                                                                proposal.readonly
                                                            "
                                                        />
                                                        {{ q.answer_two }}
                                                    </li>
                                                    <br />
                                                    <li
                                                        v-if="q.answer_three"
                                                        class="list-inline-item"
                                                    >
                                                        <input
                                                            :id="
                                                                answer_three +
                                                                q.id
                                                            "
                                                            ref="Checkbox"
                                                            v-model="q.selected"
                                                            class="form-check-input"
                                                            type="radio"
                                                            :value="
                                                                answer_three
                                                            "
                                                            :name="
                                                                'option' + q.id
                                                            "
                                                            data-parsley-required
                                                            :disabled="
                                                                proposal.readonly
                                                            "
                                                        />
                                                        {{ q.answer_three }}
                                                    </li>
                                                    <br />
                                                    <li
                                                        v-if="q.answer_four"
                                                        class="list-inline-item"
                                                    >
                                                        <input
                                                            :id="
                                                                answer_four +
                                                                q.id
                                                            "
                                                            ref="Checkbox"
                                                            v-model="q.selected"
                                                            class="form-check-input"
                                                            type="radio"
                                                            :value="answer_four"
                                                            :name="
                                                                'option' + q.id
                                                            "
                                                            data-parsley-required
                                                            :disabled="
                                                                proposal.readonly
                                                            "
                                                        />
                                                        {{ q.answer_four }}
                                                    </li>
                                                    <br
                                                        v-if="
                                                            showResult &&
                                                            q.is_correct
                                                        "
                                                    />
                                                    <li
                                                        v-if="
                                                            showResult &&
                                                            q.is_correct
                                                        "
                                                        class="list-inline"
                                                    >
                                                        <label
                                                            style="color: green"
                                                            ><i
                                                                class="fa fa-check"
                                                            ></i
                                                            >Correct</label
                                                        >
                                                    </li>
                                                    <br
                                                        v-if="
                                                            !q.is_correct &&
                                                            showResult
                                                        "
                                                    />
                                                    <li
                                                        v-if="
                                                            !q.is_correct &&
                                                            showResult
                                                        "
                                                        class="list-inline"
                                                    >
                                                        <label
                                                            style="color: red"
                                                            ><i
                                                                class="fa fa-times"
                                                            ></i
                                                            >Incorrect</label
                                                        >
                                                    </li>
                                                    <br v-if="showAnswer" />
                                                    <li
                                                        v-if="showAnswer"
                                                        class="list-inline"
                                                    >
                                                        <label
                                                            style="color: blue"
                                                            >{{
                                                                q.correct_answer_value
                                                            }}</label
                                                        >
                                                    </li>
                                                </ul>
                                            </div>
                                        </div>
                                    </ul>
                                </form>
                            </div>
                            <div class="row">
                                <div class="col-sm-12">
                                    <input
                                        v-if="
                                            !proposal.applicant_training_completed &&
                                            !proposal.readonly
                                        "
                                        type="button"
                                        class="btn btn-primary pull-right"
                                        value="Check Answers"
                                        @click.prevent="checkAnswers"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { api_endpoints, helpers } from '@/utils/hooks';

export default {
    props: {
        proposal: {
            type: Object,
            required: true,
        },
    },
    data: function () {
        let vm = this;
        return {
            values: null,
            questions: null,
            pBody: 'pBody' + vm._uid,
            showResult: false,
            showAnswer: false,
            attempt: 1,
            global_settings: [],
            answer_one: 'answer_one',
            answer_two: 'answer_two',
            answer_three: 'answer_three',
            answer_four: 'answer_four',
            hasErrors: false,
            errorString: '',
        };
    },
    computed: {
        training_doc_url: function () {
            let vm = this;
            if (vm.global_settings) {
                for (var i = 0; i < vm.global_settings.length; i++) {
                    if (
                        vm.global_settings[i].key == 'online_training_document'
                    ) {
                        return vm.global_settings[i].value;
                    }
                }
            }
            return '';
        },
        showError: function () {
            var vm = this;
            return vm.hasErrors;
        },
        allAnswered: function () {
            return this.checkAllAnswered();
        },
    },
    mounted: function () {
        let vm = this;
        vm.fetchQuestions();
        vm.fetchGlobalSettings();
    },
    methods: {
        fetchQuestions: function () {
            let vm = this;
            vm.$http.get('/api/questions/events_questions_list.json').then(
                (response) => {
                    vm.questions = response.body;
                    for (var i = 0; i < vm.questions.length; i++) {
                        vm.questions[i].is_correct = false;
                        vm.questions[i].selected = null;
                    }
                },
                (error) => {
                    console.log(error);
                }
            );
        },
        checkAllAnswered: function () {
            let vm = this;
            var answered = true;
            for (var i = 0; i < vm.questions.length; i++) {
                if (vm.questions[i].selected == null) {
                    answered = false;
                }
            }
            return answered;
        },
        checkAnswers: function () {
            let vm = this;
            vm.hasErrors = false;
            vm.errorString = '';
            if (vm.checkAllAnswered()) {
                var all_correct = true;
                vm.showResult = false;
                vm.showAnswer = false;
                for (var i = 0; i < vm.questions.length; i++) {
                    if (
                        vm.questions[i].selected ==
                        vm.questions[i].correct_answer
                    ) {
                        vm.questions[i].is_correct = true;
                    } else {
                        vm.questions[i].is_correct = false;
                        all_correct = false;
                    }
                }
                if (vm.attempt == 1) {
                    vm.showResult = true;
                } else {
                    vm.showResult = true;
                    vm.showAnswer = true;
                }
                if (all_correct == true) {
                    vm.proposal.training_completed = true;
                    vm.updateTrainingFlag();
                }
                vm.attempt++;
            } else {
                vm.errorString = 'Please answer all the questions.';
                vm.hasErrors = true;
            }
        },
        updateTrainingFlag: function () {
            let vm = this;
            vm.$http
                .post(
                    helpers.add_endpoint_json(
                        api_endpoints.proposals,
                        vm.proposal.id + '/update_training_flag'
                    ),
                    JSON.stringify({ training_completed: true })
                )
                .then(
                    (response) => {
                        vm.proposal.training_completed =
                            response.body['training_completed'];
                        vm.proposal.applicant_training_completed =
                            response.body['training_completed'];
                    },
                    (error) => {
                        swal(
                            'Application Error',
                            helpers.apiVueResourceError(error),
                            'error'
                        );
                    }
                );
        },
        fetchGlobalSettings: function () {
            let vm = this;
            vm.$http.get('/api/global_settings.json').then(
                (response) => {
                    vm.global_settings = response.body;
                },
                (error) => {
                    console.log(error);
                }
            );
        },
    },
};
</script>

<style lang="css" scoped></style>
