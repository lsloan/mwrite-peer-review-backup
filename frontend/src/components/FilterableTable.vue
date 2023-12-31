<template>
    <div>
        <div class="mdl-grid" v-if="tableName">
            <div class="mdl-cell mdl-cell--12-col">
                <h1 class="title">{{ tableName }}</h1>
            </div>
        </div>
        <div class="mdl-grid" v-if="tableControls.length > 0">
            <!-- TODO this section needs to be broken up into separate components -->
            <div v-for="{controlType, key, data} in tableControls"
                 :key="key"
                 class="filter-container mdl-cell mdl-cell--3-col mdl-cell--3-col-tablet mdl-cell--4-col-phone">

                <!-- filter types -->
                <div v-if="controlType === 'filter' && data.filter.type === 'absolute'" class="mdl-textfield flexbox">
                    <input v-model="filterValues[data.key]"
                            class="mdl-textfield__input clickable absolute-filter"
                            type="text"
                            placeholder="Search for a student">
                    <i class="material-icons filter-icon">search</i>
                </div>
                <div v-else-if="controlType === 'filter' && data.filter.type === 'choices'"
                     class="mdl-textfield">
                    <dropdown
                        :id="key"
                        label="Section Filter"
                        v-model="filterValues[data.key]"
                        :options="data.filter.makeFilterChoices(entries)"
                        :disabled="false"/>
                </div>

                <!-- control types -->
                <div v-if="controlType === 'control' && data.type === 'button'" class="control-button">
                    <button type="button"
                            class="mdl-button mdl-js-button mdl-button--raised mdl-js-ripple-effect mdl-button--accent"
                            @click="data.eventBus.$emit(data.event)">
                        {{ data.caption }}
                    </button>
                </div>
            </div>
            <div class="mdl-cell mdl-cell--6-col mdl-cell--2-col-tablet mdl-cell--hide-phone"></div>
        </div>
        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--12-col x-scrollable">
                <table class="mdl-data-table mdl-js-data-table student-table">
                    <thead>
                        <tr class="no-top-border">
                            <th v-for="{key, description} in columnMapping"
                                :key="key"
                                class="mdl-data-table__cell--non-numeric table-heading">
                                {{ description }}
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-if="isLoading">
                            <td :colspan="columnMapping.length" class="centralized student-table-cell">
                                <mdl-spinner single-color></mdl-spinner>
                            </td>
                        </tr>
                        <tr v-else
                            v-on:click="clickRow(row.id)"
                            v-for="row in paginatedFilteredEntries" :key="row.index"
                            :class="resolveRowClasses(row)">
                            <td v-for="{key, transform, component} in columnMapping"
                                :key="key"
                                :class="tableCellClasses">
                                <component v-if="component" :is="component" v-bind="transform(row)"/>
                                <template v-else>{{ transform(row[key]) }}</template>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div v-if="isLoading === false && buttonsToShow.length > 1"
                 class="flexbox pagination-container x-scrollable">
                <button class="pagination-button" type="button" v-on:click="goToPrevPage">Prev</button>

                <div v-for="(currentButton, index) in buttonsToShow" v-bind:key="index">
                    <span v-if="currentButton==='...'" class="page-gap">{{currentButton}}</span>
                    <button class="pagination-button" v-else type="button" v-on:click="goToPage(currentButton)"
                            v-bind:class="{'current-page': currentButton === currentPage}"
                            :disabled="currentButton === currentPage">
                        {{currentButton}}
                    </button>
                </div>

                <button class="pagination-button" type="button" v-on:click="goToNextPage">Next</button>
            </div>
        </div>
    </div>
</template>

<script>
import * as R from 'ramda';
import {MdlSpinner} from 'vue-mdl';
import Dropdown from '@/components/Dropdown';

const resolveClassPredicateEntry = (row, [klass, predicate]) => {
  const truthValue = typeof predicate === 'function'
    ? predicate(row)
    : predicate;
  return [klass, truthValue];
};

export default {
  name: 'FilterableTable',
  props: {
    tableName: String,
    entries: Array,
    isLoading: Boolean,
    columnMapping: Array,
    rowClasses: {
      type: Object,
      default: () => ({})
    },
    rowClickHandler: Function,
    makeRowLink: Function,
    filterSessionStorageKey: String,
    controls: {
      type: Array,
      default: () => ([])
    }
  },
  components: {MdlSpinner, Dropdown},
  data() {
    return {
      rowsPerPage: 20,
      currentPage: 1,
      numPageShow: 3,
      filterValues: {}
    };
  },
  computed: {
    rowsAreClickable() {
      return Boolean(this.rowClickHandler);
    },
    tableCellClasses() {
      return {
        'mdl-data-table__cell--non-numeric': true,
        'student-table-cell': true,
        'clickable': this.rowsAreClickable
      };
    },
    tableControls() {
      const filterControls = this.filterableColumns.map(c => ({
        key: c.key,
        controlType: 'filter',
        data: c
      }));
      const controls = this.controls.map(c => ({
        key: c.key,
        controlType: 'control',
        data: c
      }));
      return R.reverse(R.concat(filterControls, controls));
    },
    filterableColumns() {
      return this.columnMapping.filter(({filter = null}) => filter);
    },
    filterPredicate() {
      const columnsWithFilterValues = this.filterableColumns.filter(c => this.filterValues[c.key]);
      const predicates = columnsWithFilterValues.map(c => {
        const filterValue = this.filterValues[c.key];
        return R.partial(c.filter.predicate, [filterValue]);
      });
      return R.allPass(predicates);
    },
    filteredEntries() {
      return R.filter(this.filterPredicate, this.entries);
    },
    paginatedFilteredEntries() {
      const allFilteredData = this.filteredEntries;
      const startIndex = this.rowsPerPage * (this.currentPage - 1);
      const endIndex = this.rowsPerPage * this.currentPage - 1;
      return allFilteredData.slice(startIndex, endIndex + 1);
    },
    lastPage() {
      return Math.ceil(this.filteredEntries.length / this.rowsPerPage);
    },
    buttonsToShow() {
      let pagesArray = [];

      if(this.currentPage - this.numPageShow > 1) {
        pagesArray.push(1);
      }
      if(this.currentPage - this.numPageShow > 2) {
        pagesArray.push('...');
      }
      const blockBefore = this.customRange(this.currentPage - this.numPageShow, this.currentPage);

      pagesArray = pagesArray.concat(blockBefore);

      pagesArray.push(this.currentPage);

      const blockAfter = this.customRange(this.currentPage + 1, this.currentPage + this.numPageShow + 1);

      pagesArray = pagesArray.concat(blockAfter);

      if(this.currentPage + this.numPageShow < this.lastPage - 1) {
        pagesArray.push('...');
      }
      if(this.currentPage + this.numPageShow < this.lastPage) {
        pagesArray.push(this.lastPage);
      }

      while(pagesArray.length < (2 * this.numPageShow + 5) && this.lastPage > (2 * this.numPageShow + 5)) {
        if(pagesArray[1] === '...') {
          pagesArray.splice(2, 0, pagesArray[2] - 1);
        }
        if(pagesArray[(pagesArray.length - 2)] === '...') {
          pagesArray.splice((pagesArray.length - 2), 0, pagesArray[(pagesArray.length - 3)] + 1);
        }
      }

      return pagesArray;
    }
  },
  methods: {
    resolveRowClasses(row) {
      const resolveEntry = R.partial(resolveClassPredicateEntry, [row]);
      const resolver = R.pipe(
        R.toPairs,
        R.map(resolveEntry),
        R.fromPairs
      );
      return resolver(this.rowClasses);
    },
    restoreSavedFilterValues() {
      const savedFilterValues = JSON.parse(sessionStorage.getItem(this.filterSessionStorageKey));
      if(savedFilterValues) {
        this.filterValues = savedFilterValues;
      }
    },
    storeFilterValues() {
      const keyValuePairs = this.columnMapping
        .filter(cm => cm.filter && cm.filter.saveToSessionStorage)
        .map(cm => [cm.key, this.filterValues[cm.key]])
        .filter(([key, value]) => value);
      const storableFilterValues = R.fromPairs(keyValuePairs);
      if(!R.isEmpty(storableFilterValues)) {
        window.sessionStorage.setItem(this.filterSessionStorageKey, JSON.stringify(storableFilterValues));
      }
    },
    initializeFilterValues() {
      this.filterValues = this.filterableColumns.reduce((acc, next) => {
        acc[next.key] = next.filter.defaultValue;
        return acc;
      }, {});
    },
    goToNextPage() {
      if(this.currentPage < this.lastPage) {
        this.currentPage = this.currentPage + 1;
      }
    },
    goToPrevPage() {
      if(this.currentPage > 1) {
        this.currentPage = this.currentPage - 1;
      }
    },
    goToPage(pageNum) {
      if(pageNum >= 1 && pageNum <= this.lastPage) {
        this.currentPage = pageNum;
      }
    },
    customRange(startNum, endNum) {
      const range = [];
      if(startNum < 1) {
        startNum = 1;
      }
      for(let i = startNum; i < endNum; i++) {
        if(i > this.lastPage) {
          return range;
        }
        range.push(i);
      }

      return range;
    },
    clickRow(rowId) {
      if(this.rowsAreClickable) {
        this.rowClickHandler(rowId);
      }
    }
  },
  watch: {
    filteredEntries() {
      this.goToPage(1);
    },
    filterValues: {
      deep: true,
      handler() {
        if(!this.isLoading) {
          this.storeFilterValues();
        }
      }
    }
  },
  mounted() {
    this.initializeFilterValues();
    this.restoreSavedFilterValues();
  }
};
</script>

<style scoped>
    .filter-container {
        padding-left: 24px;
    }

    .control-button {
        padding: 20px 0;
    }

    .title {
        font-size: 30px;
        font-weight: 700;
    }

    .flexbox {
        display: flex;
    }

    .clickable:hover {
        cursor: pointer;
    }

    .clickable >>> input:hover {
        cursor: pointer;
    }

    .absolute-filter {
        z-index: 10;
    }

    .filter-icon {
        margin-left: -30px;
    }

    .x-scrollable {
        overflow-x: scroll;
    }

    .student-table {
        width: 100%;
        border-style: solid hidden;
    }

    .student-table-cell {
        font-size: 15px;
    }

    .no-top-border {
        border-top-style: hidden;
    }

    .table-heading {
        font-size: 18px;
        color: black;
        white-space: initial;
    }

    .centralized {
        text-align: center;
    }

    .plain-link, .plain-link:hover, .plain-link:focus {
        color: black;
        text-decoration: none;
    }

    .pagination-button {
        cursor: pointer;
        margin: 0.75em;
        padding: 0.75em;
        min-width: 3em;
        min-height: 3em;
    }

    .pagination-button:hover {
        background-color: lightgray;
    }

    .pagination-container {
        margin: auto;
    }

    .page-gap {
        cursor: text;
        display: inline-block;
        margin: auto;
        padding: 0.75em;
        text-align: center;
        vertical-align: text-top;
    }
</style>
