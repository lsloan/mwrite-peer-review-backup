<template>
    <div class="mdl-grid">
        <div class="mdl-cell mdl-cell--3-col mdl-cell--1-col-tablet"></div>
        <div class="mdl-card mdl-shadow--2dp mdl-cell mdl-cell--6-col mdl-cell--6-col-tablet mdl-cell-4-col-phone">
            <div class="mdl-card__title">
                <h2 class="mdl-card__title-text">We're Sorry</h2>
            </div>
            <div class="mdl-card__supporting-text">
                <p v-html="errorMessage"></p>
                <p>For additional help, email M-Write Support: <a href="mailto:mwrite.support@umich.edu">mwrite.support@umich.edu</a>.</p>
            </div>
            <div class="mdl-card__actions mdl-card--border">
                <a class="mdl-button mdl-button--colored mdl-js-button mdl-js-ripple-effect"
                   href="mailto:mwrite.support@umich.edu">
                    Email M-Write Support
                </a>
            </div>
        </div>
        <div class="mdl-cell mdl-cell--3-col mdl-cell--1-col-tablet"></div>
    </div>
</template>

<script>
export default {
  name: 'error',
  props: {
    errorMessage: {
      type: String,
      default: 'Something went wrong.  Please try again later.'
    }
  }
};
</script>

<style scoped>
    h2 {
        letter-spacing: -0.48px;
        padding: 0;
    }
</style>
