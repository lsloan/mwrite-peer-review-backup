<template>
    <div class='mdl-card__supporting-text datetime-container'>
        <p>{{ descriptionText }}</p>
        <div>
            <datepicker
                    format='MMM d yyyy'
                    placeholder='Day'
                    :disabled-dates='disabledDates'
                    :disabled='dateTimeDisabled'
                    v-model='models.selectedDate'>
            </datepicker>
        </div>
        <div>
            <mdl-select
                    :id="'hour-select-' + idSuffix"
                    label='Hour'
                    v-model='models.selectedHour'
                    :disabled='dateTimeDisabled'
                    :options='HOUR_CHOICES'>
            </mdl-select>
        </div>
        <div>
            <mdl-select
                    :id="'minute-select-' + idSuffix"
                    label='Minute'
                    v-model='models.selectedMinute'
                    :disabled='dateTimeDisabled'
                    :options='MINUTE_CHOICES'>
            </mdl-select>
        </div>
        <div>
            <mdl-select
                    :id="'ampm-select-' + idSuffix"
                    label='AM / PM'
                    v-model='models.selectedMeridian'
                    :disabled='dateTimeDisabled'
                    :options='MERIDIAN_CHOICES'>
            </mdl-select>
        </div>
    </div>
</template>

<script>
import * as R from 'ramda';
import moment from 'moment';

import Datepicker from 'vuejs-datepicker';
import { MdlSelect } from 'vue-mdl';

export default {
  components: { Datepicker, MdlSelect },
  name: 'DateTimePicker',
  props: [
    'id-suffix',
    'value',
    'text',
    'disabled',
    'available-start-date',
    'available-end-date'
  ],
  data() {
    return {
      descriptionText: this.text || 'Enter a custom date:',

      models: {
        selectedDate: (this.value) ? this.value.local().toDate() : null,
        selectedHour: (this.value) ? this.value.local().format('h') : '11',
        selectedMinute: (this.value) ? this.value.local().format('mm') : '45',
        selectedMeridian: (this.value) ? this.value.local().format('a').toUpperCase() : 'PM'
      },

      HOUR_CHOICES: R.range(1, 13).map(i => i.toString()),
      MINUTE_CHOICES: ['00', '15', '30', '45'],
      MERIDIAN_CHOICES: ['AM', 'PM']
    };
  },
  computed: {
    dateTimeDisabled() {
      return this.disabled;
    },
    disabledDates() {
      if(!this.availableStartDate && !this.availableEndDate) {
        return {};
      }

      let interval = {};
      if(this.availableStartDate) {
        interval['to'] = this.availableStartDate.local().toDate();
      }
      if(this.availableEndDate) {
        interval['from'] = this.availableEndDate.local().toDate();
      }

      return interval;
    },
    dateTimeValue() {
      const {
        selectedDate: date,
        selectedHour: hour,
        selectedMinute: minute,
        selectedMeridian: meridian
      } = this.models;

      if(date && hour && minute && meridian) {
        const hours12 = parseInt(hour);
        const hours24 =
          meridian === 'AM'
            ? hours12 === 12 ? 0 : hours12
            : hours12 === 12 ? 12 : hours12 + 12;
        const minutes = parseInt(minute);
        return moment(date)
          .hours(hours24)
          .minutes(minutes)
          .utc();
      }
      else {
        return null;
      }
    }
  },
  watch: {
    dateTimeValue(newValue, oldValue) {
      if(newValue !== oldValue) {
        this.$emit('input', newValue);
      }
    }
  }
};
</script>

<style scoped>
.vdp-datepicker input[type='text'] {
  font-size: 14px;
  padding: 1%;
  max-width: 120px;
}

.datetime-container > div,
.datetime-container .vdp-datepicker,
.datetime-container .vdp-datepicker div {
  display: inline;
}

.datetime-container >>> .vdp-datepicker input {
  padding: 8px;
  margin-bottom: 6px;
  font-size: 14px;
}

.datetime-container .mdl-textfield {
  width: 80px;
  margin-left: 3px;
  margin-right: 3px;
}

.mdl-textfield {
  width: 100%;
}
</style>
