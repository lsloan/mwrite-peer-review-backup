<template>
    <form id="rubric-form" @submit.prevent>
        <template v-if="reviewIsInProgress">
            <div class="mdl-grid">
                <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
                <mdl-card
                        class="no-min-height-rubric-card mdl-shadow--2dp mdl-cell mdl-cell--10-col mdl-cell--6-col-tablet mdl-cell-2-col-phone"
                        supporting-text="Reviews are in progress, so this rubric is now read-only."></mdl-card>
                <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
            </div>
        </template>

        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
            <mdl-card
                class="no-min-height-rubric-card mdl-shadow--2dp mdl-cell mdl-cell--10-col mdl-cell--6-col-tablet mdl-cell-2-col-phone"
                title="Peer Review"
                supporting-text="slot">
                <div slot="supporting-text">
                    <div class="mdl-card__supporting-text">
                        <p>
                            <template v-if="peerReviewDueDate">
                                Peer reviews
                                <template v-if="reviewIsInProgress">are</template>
                                <template v-else>will be</template>
                                due on {{ peerReviewDueDateDisplay }}.
                            </template>
                            <template v-else>
                                You have not selected a peer review due date in Canvas.  You can proceed anyway if that's
                                what was intended.
                            </template>
                        </p>
                    </div>
                </div>
            </mdl-card>
            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
        </div>

        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>

            <!-- TODO pull this out into its own component -->
            <!-- TODO double check markup vs the below -->
            <mdl-card
                    id="prompt-card"
                    class="mdl-shadow--2dp mdl-cell mdl-cell--10-col mdl-cell--6-col-tablet mdl-cell-2-col-phone"
                    title="Writing Prompt"
                    supporting-text="slot">
                <div slot="supporting-text">
                    <div class="mdl-card__supporting-text">
                        <dropdown
                                id="prompt-menu"
                                label="The rubric will be applied to the following assignment:"
                                v-model="models.selectedPrompt"
                                :options="promptChoices"
                                :disabled="reviewIsInProgress"
                                empty-caption="Select an assignment">
                        </dropdown>
                        <p v-if="promptSection && promptDueDateDisplay" class="assignment-info">
                            This prompt is assigned to {{ promptSection }} and is due {{ promptDueDateDisplay }}.
                        </p>
                    </div>

                    <!-- TODO this could be abstracted into its own component -->
                    <div v-if="promptIssues.length > 0" class="mdl-card__supporting-text validations-container">
                        <ul class="mdl-list">
                            <li v-for="(issue, index) in promptIssues" :key="index" class="mdl-list__item">
                                <span class="mdl-list__item-primary-content">
                                    <i v-if="issue.fatal" class="material-icons mdl-list__item-icon">warning</i>
                                    <i v-else class="material-icons mdl-list__item-icon">error_outline</i>
                                    {{ issue.message }}
                                </span>
                            </li>
                        </ul>
                    </div>

                </div>
            </mdl-card>

            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
        </div>

        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
            <mdl-card
                    class="mdl-card mdl-shadow--2dp mdl-cell mdl-cell--10-col mdl-cell--6-col-tablet mdl-cell-2-col-phone"
                    title="Peer Review Open Date"
                    supporting-text="slot">
                <div slot="supporting-text">
                    <div class="mdl-card__supporting-text">
                        <mdl-switch v-model="models.peerReviewOpenDateIsPromptDueDate" :disabled="reviewIsInProgress">
                            Use the writing prompt's due date as the peer review open date
                        </mdl-switch>
                    </div>
                    <date-time-picker v-if="!models.peerReviewOpenDateIsPromptDueDate"
                        id-suffix="peer-review-open-date-time"
                        text="Please select the peer review open date:"
                        :disabled="reviewIsInProgress"
                        :available-start-date="promptDueDate"
                        :available-end-date="peerReviewDueDate"
                        v-model="models.peerReviewOpenDateTime" />
                    <div class="mdl-card__supporting-text">
                        <p v-if="peerReviewOpenDateIsValid">
                            Peer reviews will be distributed at {{ peerReviewOpenDateDisplay }}.  Students who have
                            not completed the writing prompt assignment in Canvas by this date will be unable
                            to participate in peer review.
                        </p>
                        <p v-else-if="!models.peerReviewOpenDateIsPromptDueDate">
                            The peer review open date must be between the prompt assignments's due date and the peer review's due date.
                        </p>
                    </div>
                </div>
            </mdl-card>

            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
        </div>

        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
            <mdl-card
                    class="mdl-card mdl-shadow--2dp mdl-cell mdl-cell--10-col mdl-cell--6-col-tablet mdl-cell-2-col-phone"
                    title="Peer Review Evaluations"
                    supporting-text="slot">
                <div slot="supporting-text">
                    <div class="mdl-card__supporting-text">
                        <mdl-switch v-model="models.peerReviewEvaluationIsMandatory" :disabled="reviewIsInProgress">
                            Mandatory
                        </mdl-switch>
                    </div>
                    <date-time-picker v-if="models.peerReviewEvaluationIsMandatory"
                        id-suffix="peer-review-evaluation-due-date-time"
                        text="Please select the peer review evaluation due date:"
                        :disabled="reviewIsInProgress"
                        :available-start-date="peerReviewEvaluationDueDateBeginningBound"
                        v-model="models.peerReviewEvaluationDueDateTime" />
                    <div class="mdl-card__supporting-text">
                        <p v-if="models.peerReviewEvaluationIsMandatory">
                            <template v-if="peerReviewEvaluationDueDateIsValid">
                                Peer review evaluations
                                <template v-if="reviewIsInProgress">are</template>
                                <template v-else>will be</template>
                                due at {{ peerReviewEvaluationDueDateDisplay }}.
                            </template>
                            <template v-else>
                                Please select a peer review evaluation due date after the
                                <template v-if="peerReviewDueDate">
                                    peer review due date ({{ peerReviewDueDateDisplay }})
                                </template>
                                <template v-else>
                                    peer review open date ({{ peerReviewOpenDateDisplay }})
                                </template>
                                .
                            </template>
                        </p>
                        <p v-else>
                            Peer review evaluations
                            <template v-if="reviewIsInProgress">
                                are
                            </template>
                            <template v-else>
                                will be
                            </template>
                            optional and
                            <template v-if="reviewIsInProgress">
                                do
                            </template>
                            <template v-else>
                                will
                            </template>
                            not have a due date.
                        </p>
                    </div>
                </div>
            </mdl-card>

            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
        </div>

        <template v-if="!(reviewIsInProgress && !models.selectedRevision.value)">
            <div class="mdl-grid">
                <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>

                <!-- TODO pull this out into its own component -->
                <!-- TODO double check markup vs the above -->
                <mdl-card
                        class="mdl-card mdl-shadow--2dp mdl-cell mdl-cell--10-col mdl-cell--6-col-tablet mdl-cell-2-col-phone"
                        title="Revision"
                        supporting-text="slot">
                    <div slot="supporting-text">
                        <div class="mdl-card__supporting-text">
                            <dropdown
                                    id="revision-menu"
                                    label="If students will be completing a revision, please select the revision assignment here."
                                    v-model="models.selectedRevision"
                                    :options="revisionChoices"
                                    :disabled="reviewIsInProgress">
                            </dropdown>
                            <p v-if="revisionSection && revisionDueDateDisplay" class="assignment-info">
                                This revision is assigned to {{ revisionSection }} and is due {{ revisionDueDateDisplay }}.
                            </p>
                        </div>

                        <!-- TODO this could be abstracted into its own component -->
                        <div v-if="revisionIssues.length > 0" class="mdl-card__supporting-text validations-container">
                            <ul class="mdl-list">
                                <li v-for="(issue, index) in revisionIssues" :key="index" class="mdl-list__item">
                                    <span class="mdl-list__item-primary-content">
                                        <i v-if="issue.fatal" class="material-icons mdl-list__item-icon">warning</i>
                                        <i v-else class="material-icons mdl-list__item-icon">error_outline</i>
                                        {{ issue.message }}
                                    </span>
                                </li>
                            </ul>
                        </div>

                    </div>
                </mdl-card>

                <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
            </div>
        </template>

        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
            <mdl-card
                    class="mdl-card mdl-shadow--2dp mdl-cell mdl-cell--10-col mdl-cell--6-col-tablet mdl-cell-2-col-phone"
                    title="Description"
                    supporting-text="slot">
                <div slot="supporting-text" class="mdl-card__supporting-text">
                    <autosize-textarea
                        class="all-input"
                        v-model="models.description"
                        label="Enter a description for this rubric here."
                        :disabled="reviewIsInProgress"/>
                </div>
            </mdl-card>
            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
        </div>
        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
            <mdl-card
                    class="mdl-card mdl-shadow--2dp mdl-cell mdl-cell--10-col mdl-cell--6-col-tablet mdl-cell-2-col-phone"
                    title="Criteria"
                    supporting-text="slot"
                    :actions="!reviewIsInProgress ? 'slot' : ''">
                <div slot="supporting-text" class="criteria-container mdl-card__supporting-text">
                    <mdl-card v-for="(criterion, index) in models.criteria" :key="criterion.id" class="criterion-card mdl-shadow--2dp" supporting-text="slot">
                        <div slot="supporting-text">
                            <div v-if="!reviewIsInProgress && index > 0" class="criterion-delete-button-container">
                                <button type="button" class="mdl-chip__action" tabindex="-1" @click="removeCriterion(criterion.id)">
                                    <i class="material-icons">cancel</i>
                                </button>
                            </div>
                            <div class="mdl-card__supporting-text">
                                <autosize-textarea
                                    class="all-input"
                                    v-model="criterion.description"
                                    :value="`${criterion.description}`"
                                    label="Enter a description for this criterion here."
                                    :disabled="reviewIsInProgress"/>
                            </div>
                        </div>
                    </mdl-card>
                </div>
                <div slot="actions" class="mdl-card__actions">
                    <button type="button"
                            class="mdl-button mdl-js-button mdl-button--fab mdl-button--mini-fab mdl-button--colored"
                            @click="addCriterion">
                        <i class="material-icons">add</i>
                    </button>
                </div>
            </mdl-card>
            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
        </div>
        <template v-if="!reviewIsInProgress">
            <div class="mdl-grid">
                <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
                <div class="mdl-cell mdl-cell--10-col mdl-cell--6-col-tablet mdl-cell-2-col-phone">
                    <button
                            class="mdl-button mdl-js-button mdl-button--raised mdl-js-ripple-effect mdl-button--accent"
                            type="submit"
                            :disabled="!rubricIsValid || submissionInProgress"
                            @click="submitRubricForm">
                        Submit
                    </button>
                </div>
                <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
            </div>
            <div class="mdl-grid">
                <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
                <div class="mdl-cell mdl-cell--10-col mdl-cell--6-col-tablet mdl-cell-2-col-phone">
                    <snackbar display-on="notification"/>
                </div>
                <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
            </div>
        </template>
    </form>
</template>

<script>
import * as R from 'ramda';
import moment from 'moment';
import {MdlCard, MdlSwitch, MdlSelect} from 'vue-mdl';

import {default as Snackbar, notificationTime} from '@/components/Snackbar';
import Dropdown from '@/components/Dropdown';
import DateTimePicker from '@/components/DateTimePicker';
import AutosizeTextarea from '@/components/AutosizeTextarea';

import api from '@/services/api';
import {gensym} from '@/services/util';
import {validationInfoAsIssues} from '@/services/validation';

const utcMomentIfNotNil = R.unless(R.isNil, moment.utc);

const makeCriterion = (prefix = 'criterion', description = '') => {
  return {
    id: gensym(prefix),
    description: description
  };
};

const makeAssignmentOptions = (assignmentNamesById, ...excludedAssignmentIds) => R.pipe(
  R.toPairs,
  R.reject(([id, _]) => R.any(exId => id === exId, excludedAssignmentIds)),
  R.map(([id, name]) => ({value: id, name: name})),
  R.sortBy(R.prop('id'))
)(assignmentNamesById);

const NO_REVISION_OPTION = {value: null, name: 'No revision'};
const DISPLAY_DATE_FORMAT = 'MMM D YYYY h:mm A';

const RUBRIC_UPDATE_SUCCESS_MESSAGE = 'The rubric was successfully created.  You will be returned to the dashboard.';
const RUBRIC_UPDATE_FAILURE_MESSAGE = 'An error occurred.  Please try again later.';

const REDIRECT_TIME = notificationTime(RUBRIC_UPDATE_SUCCESS_MESSAGE);

export default {
  components: {Dropdown, DateTimePicker, AutosizeTextarea, MdlCard, MdlSwitch, MdlSelect, Snackbar},
  props: ['peer-review-assignment-id'],
  data() {
    return {
      assignmentNamesById: {},
      existingRubric: null,
      validations: {},
      peerReviewDueDate: null,

      models: {
        criteria: [makeCriterion()],
        description: '',
        peerReviewOpenDateTime: null,
        peerReviewOpenDateIsPromptDueDate: true,
        peerReviewEvaluationDueDateTime: null,
        peerReviewEvaluationIsMandatory: false,
        selectedPrompt: null,
        selectedRevision: NO_REVISION_OPTION
      },
      submissionInProgress: false
    };
  },
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    reviewIsInProgress() {
      return Boolean(this.existingRubric && this.existingRubric.reviewInProgress);
    },
    selectedPromptId() {
      return this.models.selectedPrompt && this.models.selectedPrompt.value;
    },
    selectedRevisionId() {
      return this.models.selectedRevision && this.models.selectedRevision.value;
    },
    promptChoices() {
      return makeAssignmentOptions(
        this.assignmentNamesById,
        this.selectedPromptId,
        this.selectedRevisionId
      );
    },
    revisionChoices() {
      const revisionOptions = makeAssignmentOptions(
        this.assignmentNamesById,
        this.selectedPromptId,
        this.selectedRevisionId
      );
      return this.selectedRevisionId
        ? [NO_REVISION_OPTION].concat(revisionOptions)
        : revisionOptions;
    },
    promptIssues() {
      return this.selectedPromptId
        ? validationInfoAsIssues(this.validations[this.selectedPromptId], true)
        : [];
    },
    revisionIssues() {
      return this.selectedRevisionId
        ? validationInfoAsIssues(this.validations[this.selectedRevisionId], false)
        : [];
    },
    promptSection() {
      if(this.selectedPromptId) {
        const validations = this.validations[this.selectedPromptId];
        return validations.sectionName || 'all students';
      }
    },
    promptDueDate() {
      if(this.selectedPromptId) {
        const {dueDateUtc} = this.validations[this.selectedPromptId];
        return moment.utc(dueDateUtc);
      }
    },
    promptDueDateDisplay() {
      if(this.promptDueDate) {
        return this.promptDueDate.local().format(DISPLAY_DATE_FORMAT);
      }
    },
    revisionSection() {
      if(this.selectedRevisionId) {
        const {sectionName} = this.validations[this.selectedRevisionId];
        return sectionName || 'all students';
      }
    },
    revisionDueDate() {
      if(this.selectedRevisionId) {
        const {dueDateUtc} = this.validations[this.selectedRevisionId];
        return moment.utc(dueDateUtc);
      }
    },
    revisionDueDateDisplay() {
      if(this.revisionDueDate) {
        return this.revisionDueDate.local().format(DISPLAY_DATE_FORMAT);
      }
    },
    rubricIsValid() {
      const criteriaExist = this.models.criteria && !R.isEmpty(this.models.criteria);
      const criteriaDescriptionsExist = criteriaExist && R.all(c => !R.isEmpty(c.description), this.models.criteria);
      const criteriaAreValid = criteriaExist && criteriaDescriptionsExist;

      const allIssues = R.concat(this.promptIssues, this.revisionIssues);
      const noFatalIssuesFound = R.all(i => !i.fatal, allIssues);

      return this.models.selectedPrompt && this.models.description && criteriaAreValid && noFatalIssuesFound && this.peerReviewOpenDateIsValid && this.peerReviewEvaluationDueDateIsValid;
    },
    peerReviewOpenDisabledDates() {
      return this.promptDueDate && this.peerReviewDueDate
        ? {to: this.promptDueDate.local().toDate(), from: this.peerReviewDueDate.local().toDate()}
        : {};
    },
    peerReviewOpenDate() {
      if(this.models.peerReviewOpenDateIsPromptDueDate) {
        return this.promptDueDate;
      }
      else {
        return this.models.peerReviewOpenDateTime;
      }
    },
    peerReviewOpenDateDisplay() {
      return this.peerReviewOpenDate
        ? this.peerReviewOpenDate.local().format(DISPLAY_DATE_FORMAT)
        : '';
    },
    peerReviewOpenDateIsValid() {
      if(!this.peerReviewOpenDate) {
        return false;
      }
      else if(this.peerReviewDueDate) {
        const peerReviewDueAfterPrompt = this.peerReviewOpenDate.isSameOrAfter(this.promptDueDate);
        const peerReviewDueAfterOpening = this.peerReviewOpenDate.isSameOrBefore(this.peerReviewDueDate);
        return peerReviewDueAfterPrompt && peerReviewDueAfterOpening;
      }
      else {
        return true;
      }
    },
    peerReviewEvaluationDueDateBeginningBound() {
      return this.peerReviewDueDate
        ? this.peerReviewDueDate
        : this.peerReviewOpenDate;
    },
    peerReviewEvaluationDueDateIsValid() {
      if(!this.models.peerReviewEvaluationIsMandatory) {
        return true;
      }
      else {
        if(this.models.peerReviewEvaluationDueDateTime) {
          return this.models.peerReviewEvaluationDueDateTime.isAfter(this.peerReviewEvaluationDueDateBeginningBound);
        }
        else {
          return false;
        }
      }
    },
    peerReviewEvaluationDueDateDisplay() {
      return this.models.peerReviewEvaluationDueDateTime
        ? this.models.peerReviewEvaluationDueDateTime.local().format(DISPLAY_DATE_FORMAT)
        : '';
    },
    peerReviewDueDateDisplay() {
      return this.peerReviewDueDate
        ? this.peerReviewDueDate.local().format(DISPLAY_DATE_FORMAT)
        : '';
    }
  },
  methods: {
    fetchData() {
      return this.$api.get('/course/{}/rubric/peer_review_assignment/{}/', this.courseId, this.peerReviewAssignmentId)
        .then(r => {
          const {assignments, validationInfo, existingRubric, peerReviewDueDate} = r.data;
          this.assignmentNamesById = assignments;
          this.validations = validationInfo;
          this.existingRubric = existingRubric;
          this.peerReviewDueDate = peerReviewDueDate ? moment.utc(peerReviewDueDate) : null;
        });
    },
    initializeModels() {
      if(this.existingRubric) {
        const {promptId, revisionId, peerReviewOpenDateTime, peerReviewEvaluationDueDateTime} = this.existingRubric;
        const promptOption = {
          value: promptId,
          name: this.assignmentNamesById[promptId]
        };
        const revisionOption = this.revisionId
          ? {value: revisionId, name: this.assignmentNamesById[revisionId]}
          : NO_REVISION_OPTION;

        const modelConverter = R.pipe(
          R.dissoc('promptId'),
          R.dissoc('revisionId'),
          R.assoc('selectedPrompt', promptOption),
          R.assoc('selectedRevision', revisionOption),
          R.assoc('peerReviewOpenDateTime', moment.utc(peerReviewOpenDateTime)),
          R.assoc('peerReviewEvaluationDueDateTime', utcMomentIfNotNil(peerReviewEvaluationDueDateTime))
        );

        this.models = modelConverter(this.existingRubric);
      }
    },
    initializeBreadcrumb() {
      const prompt = this.models.selectedPrompt
        ? this.models.selectedPrompt.name
        : 'Create New';
      this.$store.commit('updateBreadcrumbInfo', {
        title: `${prompt} Rubric`,
        peerReviewAssignmentId: this.peerReviewAssignmentId
      });
    },
    addCriterion() {
      this.models.criteria.push(makeCriterion());
    },
    removeCriterion(id) {
      this.models.criteria = R.reject(c => c.id === id, this.models.criteria);
    },
    rubricUpdateSuccess() {
      this.$root.$emit('notification', RUBRIC_UPDATE_SUCCESS_MESSAGE);
      setTimeout(() => this.$router.push({name: 'InstructorDashboard'}), REDIRECT_TIME);
    },
    rubricUpdateFailure() {
      this.$root.$emit('notification', RUBRIC_UPDATE_FAILURE_MESSAGE);
    },
    submitRubricForm() {
      if(this.rubricIsValid) {
        const peerReviewEvaluationDueDate =
          this.models.peerReviewEvaluationDueDateTime && this.models.peerReviewEvaluationIsMandatory
            ? this.models.peerReviewEvaluationDueDateTime.toISOString()
            : null;
        const data = {
          promptId: parseInt(this.models.selectedPrompt.value) || null,
          revisionId: this.models.selectedRevision.value ? parseInt(this.models.selectedRevision.value) : null,
          peerReviewAssignmentId: this.peerReviewAssignmentId,
          description: R.trim(this.models.description),
          criteria: R.map(c => R.trim(c.description), this.models.criteria),
          peerReviewOpenDateIsPromptDueDate: this.models.peerReviewOpenDateIsPromptDueDate,
          peerReviewOpenDate: this.peerReviewOpenDate.toISOString(),
          peerReviewEvaluationIsMandatory: this.models.peerReviewEvaluationIsMandatory,
          peerReviewEvaluationDueDate
        };

        this.submissionInProgress = true;
        api.post('/course/{}/rubric/', data, this.courseId)
          .then(this.rubricUpdateSuccess)
          .catch(this.rubricUpdateFailure)
          .finally(() => {
            this.submissionInProgress = false;
          });
      }
      else {
        this.$root.$emit('notification', {
          message: 'This rubric is not valid.  Double check that you have selected a writing prompt, added a description, created criteria, and configured a peer review open date no sooner than the prompt\'s open date.'
        });
      }
    }
  },
  mounted() {
    this.fetchData()
      .then(this.initializeModels)
      .then(this.initializeBreadcrumb);
  }
};
</script>

<style scoped>
    form {
        width: 100%;
        height: 100%;
    }

    .hidden {
        display: none !important;
    }

    textarea {
        resize: none;
    }

    .mdl-textfield {
        width: 100%;
    }

    .all-input {
        width: 100%;
    }

    .mdl-card, .mdl-card .mdl-card__supporting-text {
        overflow: visible;
        z-index: auto;
    }

    .criterion-card {
        margin-bottom: 16px;
        width: 100%;
        min-height: 0;
    }

    .criterion-delete-button-container {
        height: 0;
    }

    .criterion-delete-button-container > button.mdl-chip__action {
        float: right;
    }

    button[type="submit"] {
        display: block;
        margin: 0 auto;
    }

    #prompt-menu, #revision-menu {
        border-bottom: 1px solid darkgray;
        border-radius: 4px;
        margin-top: 20px;
        text-transform: none;
        display: block;
        min-width: 60%;
        text-align: left;
    }

    .validations-container {
        padding-top: 0;
        padding-bottom: 0;
    }

    .validations-container span {
        font-size: 14px;
    }

    .validations-container > ul {
        margin-top: 0;
        margin-bottom: 0;
    }

    .assignment-info {
        margin-top: 25px;
    }

    .no-min-height-rubric-card {
        min-height: 0;
    }

    #rubric-form textarea[disabled], #rubric-form button[disabled][type=button] {
        color: inherit;
    }

    .vdp-datepicker input[type="text"] {
        font-size: 14px;
        padding: 1%;
        max-width: 120px;
    }

    .datetime-container > div, .datetime-container .vdp-datepicker, .datetime-container .vdp-datepicker div {
        display: inline;
    }

    .datetime-container .mdl-textfield {
        width: 80px;
        margin-left: 3px;
        margin-right: 3px;
    }

    .datetime-container >>> .vdp-datepicker input {
        padding: 8px;
        margin-bottom: 6px;
        font-size: 14px;
    }

    .mdl-card__supporting-text >>> textarea.autosize-textarea {
        color: inherit;
    }
</style>
