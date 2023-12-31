<template>
    <div>
        <peer-review-section section-number="1">
            <section>
                <h2 ref="firstHeader" tabindex="-1">Download Submission</h2>
                <mdl-anchor-button :href="submissionDownloadUrl" colored raised>
                    Download
                </mdl-anchor-button>
            </section>
        </peer-review-section>
        <peer-review-section section-number="2">
            <h2>Submit Your Review</h2>
        </peer-review-section>
        <peer-review-section>
            <p class="preserve-whitespace">{{ rubricDescription }}</p>
        </peer-review-section>
        <form @submit.prevent>
            <peer-review-section v-for="(criterion, index) in criteria" :key="criterion.id">
                <p class="preserve-whitespace" >{{ criterion.description }}</p>
                <autosize-textarea
                    class="criterion-input"
                    :label="`Enter your comment for the ${numberToOrdinal(index + 1)} criterion here.`"
                    :value="`${existingCommentForCriterion(criterion)}`"
                    :key="existingCommentsLoadedTime"
                    v-model="responses[criterion.id]"/>
            </peer-review-section>
            <peer-review-section>
                <p>Click "Save" to update review. Note that submission time will also update after saving.</p>
                <mdl-button raised colored @click.native="submitReview" :disabled="!reviewIsComplete || submissionInProgress">
                    Save
                </mdl-button>
                <mdl-button @click.native="cancelReview">
                    Cancel
                </mdl-button>
            </peer-review-section>
        </form>
        <snackbar display-on="notification"/>
    </div>
</template>

<script>
import * as R from 'ramda';
import {MdlButton, MdlAnchorButton} from 'vue-mdl';
import {toWordsOrdinal} from 'number-to-words';

import api from '@/services/api';
import {default as Snackbar, notificationTime} from '@/components/Snackbar';
import PeerReviewSection from '@/components/PeerReviewSection';
import AutosizeTextarea from '@/components/AutosizeTextarea';

const SUBMIT_REVIEW_SUCCESS_MESSAGE = 'Thank you for submitting your peer review!  You will be returned to the dashboard.';
const SUBMIT_REVIEW_ERROR_MESSAGE = 'An error occurred.  Please try again later.';
const SUBMIT_REVIEW_INCOMPLETE_MESSAGE = 'Your review is not complete.  Double check that you have entered a response for all criteria.';

const REDIRECT_TIME = notificationTime(SUBMIT_REVIEW_SUCCESS_MESSAGE);

export default {
  name: 'PeerReview',
  props: ['review-id'],
  components: {PeerReviewSection, AutosizeTextarea, Snackbar, MdlButton, MdlAnchorButton},
  data() {
    return {
      rubric: {},
      existingComments: {},
      responses: {},
      submissionInProgress: false,
      existingCommentsLoadedTime: undefined, // indicate when component needs re-render
    };
  },
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    rubricDescription() {
      return this.rubric.description || '';
    },
    criteria() {
      const {criteria = []} = this.rubric;
      return R.sortBy(c => c.id, criteria);
    },
    comments() {
      return R.toPairs(this.responses)
        .filter(([_, comment]) => R.trim(comment))
        .map(([criterionId, comment]) => ({
          criterionId: parseInt(criterionId),
          comment: R.trim(comment)
        }));
    },
    reviewIsComplete() {
      return this.criteria.length === this.comments.length;
    },
    submissionDownloadUrl() {
      return `${__API_URL__}/course/${this.courseId}/reviews/${this.reviewId}/submission`;
    }
  },
  methods: {
    numberToOrdinal(number) {
      return toWordsOrdinal(number);
    },
    existingCommentForCriterion(criterion) {
      return this.existingComments[criterion.id] || '';
    },
    submitReview() {
      if(this.reviewIsComplete) {
        const data = {comments: this.comments};
        this.submissionInProgress = true;
        api.post('/course/{}/reviews/{}/', data, this.courseId, this.reviewId)
          .then(() => {
            this.$root.$emit('notification', SUBMIT_REVIEW_SUCCESS_MESSAGE);
            setTimeout(() => this.$router.push('/student/dashboard'), REDIRECT_TIME);
          })
          .catch(() => {
            this.$root.$emit('notification', SUBMIT_REVIEW_ERROR_MESSAGE);
            this.submissionInProgress = false;
          });
      }
      else {
        this.$root.$emit('notification', SUBMIT_REVIEW_INCOMPLETE_MESSAGE);
      }
    },
    cancelReview() {
      this.$router.back();
    }
  },
  mounted() {
    this.$api.get('/course/{}/reviews/{}/rubric', this.courseId, this.reviewId).then(r => {
      this.rubric = r.data;
    });

    this.$api.get('/course/{}/reviews/{}', this.courseId, this.reviewId).then(r => {
      // make assoc. array with criterionRealId as key and comment as value
      this.existingComments = Object.fromEntries(Object.values(r.data).map(x => [x.criterionRealId, x.comment]));
      this.existingCommentsLoadedTime = Date.now(); // trigger component re-render
    });

    this.$refs.firstHeader.scrollIntoView(true);
  },
};
</script>

<style scoped>
    h2, p {
        font-family: "Roboto","Helvetica","Arial",sans-serif;
    }

    h2 {
        font-size: 24px;
        line-height: 24px;
        margin: 8px 0;
        letter-spacing: -0.02em;
    }

    p {
        font-size: 16px;
    }

    .criterion-input {
        width: 100%;
    }

    .preserve-whitespace {
        white-space: pre-wrap;
    }
</style>
