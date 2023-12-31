import Vue from 'vue';
import Router from 'vue-router';

import {redirectToRoleDashboard, authenticatedInstructorsOnly, authenticatedStudentsOnly} from './guards';

import Modal from '@/components/Modal';
import ReviewsGiven from '@/components/ReviewsGiven';
import ReviewsReceived from '@/components/ReviewsReceived';
import SingleReview from '@/components/SingleReview';
import SingleReviewForEvaluation from '@/components/SingleReviewForEvaluation';

import Error from '@/pages/Error';
import InstructorDashboard from '@/pages/InstructorDashboard';
import StudentList from '@/pages/StudentList';
import ReviewStatus from '@/pages/ReviewStatus';
import AssignmentStatus from '@/pages/AssignmentStatus';
import Rubric from '@/pages/Rubric';
import StudentDashboard from '@/pages/StudentDashboard';
import PeerReview from '@/pages/PeerReview';
import ManualDistribution from '@/pages/ManualDistribution';

Vue.use(Router);

const router = new Router({
  routes: [
    {
      path: '/',
      beforeEnter: redirectToRoleDashboard
    },
    {
      path: '/error',
      component: Error
    },
    {
      path: '/permission-denied',
      component: Error,
      props: {errorMessage: '<p style="font-size: large">Due to a browser-related error, M-Write cannot be accessed.  Troubleshooting options:</p><ul style="font-size: large"><li>Launch a <a href="https://support.google.com/chrome/answer/95464">Chrome Incognito window</a>, navigate to Canvas and try to access M-Write.</li><li><a href="https://support.google.com/accounts/answer/32050">Clear your browser cookies and cache</a> and try to access M-Write again.</li><li>Log out of Canvas and close the browser, then re-open the browser and re-login to your Canvas course to access M-Write again.</li><li>Access M-Write on a different computer.</li></ul>\n'}
    },
    {
      path: '/instructor/dashboard',
      name: 'InstructorDashboard',
      component: InstructorDashboard,
      beforeEnter: authenticatedInstructorsOnly,
      meta: {
        breadcrumbPathComponents: [{text: 'Peer Review', href: '/instructor/dashboard'}]
      }
    },
    {
      path: '/instructor/rubric/peer_review_assignment/:peerReviewAssignmentId',
      name: 'Rubric',
      component: Rubric,
      beforeEnter: authenticatedInstructorsOnly,
      props: (route) => ({peerReviewAssignmentId: route.params.peerReviewAssignmentId}),
      meta: {
        breadcrumbPathComponents: info => ([
          {text: 'Peer Review', href: '/instructor/dashboard'},
          {text: info['title'], href: `/instructor/rubric/peer_review_assignment/${info.peerReviewAssignmentId}`}
        ])
      }
    },
    {
      path: '/instructor/students',
      component: StudentList,
      beforeEnter: authenticatedInstructorsOnly,
      meta: {
        breadcrumbPathComponents: [{text: 'Students', href: '/instructor/students'}]
      }
    },
    {
      path: '/instructor/reviews/rubric/:rubricId',
      name: 'ReviewStatus',
      component: ReviewStatus,
      beforeEnter: authenticatedInstructorsOnly,
      props: (route) => ({rubricId: route.params.rubricId}),
      meta: {
        breadcrumbPathComponents: info => ([
          {text: 'Peer Review', href: '/instructor/dashboard'},
          {text: info['title'], href: `/instructor/reviews/rubric/${info.rubricId}`}
        ])
      }
    },
    {
      path: '/instructor/reviews/rubric/:rubricId/unassigned',
      name: 'UnassignedStudents',
      component: ManualDistribution,
      beforeEnter: authenticatedInstructorsOnly,
      props: route => ({rubricId: route.params.rubricId})
    },
    {
      path: '/instructor/reviews/student/:studentId',
      name: 'AssignmentStatus',
      component: AssignmentStatus,
      beforeEnter: authenticatedInstructorsOnly,
      props: route => ({studentId: parseInt(route.params.studentId)}),
      meta: {
        breadcrumbPathComponents: info => ([
          {text: 'Students', href: '/instructor/students'},
          {text: info.studentName, href: `/instructor/reviews/student/${info.studentId}`}
        ])
      }
    },
    {
      path: '/instructor/reviews/student/:studentId/rubric/:rubricId',
      name: 'AssignmentStatusForRubric',
      component: AssignmentStatus,
      beforeEnter: authenticatedInstructorsOnly,
      props: route => ({
        studentId: parseInt(route.params.studentId),
        rubricId: parseInt(route.params.rubricId)
      }),
      children: [
        {
          path: 'review/:reviewId',
          name: 'SingleReview',
          component: Modal,
          props: route => ({component: SingleReview, childProps: {reviewId: route.params.reviewId}})
        }
      ],
      meta: {
        breadcrumbPathComponents: info => ([
          {text: 'Peer Review', href: '/instructor/dashboard'},
          {text: info.peerReviewTitle, href: `/instructor/reviews/rubric/${info.rubricId}`},
          {text: info.studentName, href: `/instructor/reviews/student/${info.studentId}/rubric/${info.rubricId}`}
        ])
      }
    },
    {
      path: '/student/dashboard',
      component: StudentDashboard,
      beforeEnter: authenticatedStudentsOnly,
      children: [
        {
          path: 'student/:studentId/reviews/:rubricId/given/',
          name: 'ReviewsGiven',
          component: Modal,
          props: route => ({component: ReviewsGiven, childProps: route.params})
        },
        {
          path: 'student/:studentId/reviews/:rubricId/received/',
          name: 'ReviewsReceived',
          component: Modal,
          props: route => ({component: ReviewsReceived, childProps: route.params})
        },
        {
          path: 'student/:studentId/evaluation/:peerReviewId',
          name: 'MandatoryEvaluation',
          component: Modal,
          props: route => ({component: SingleReviewForEvaluation, childProps: route.params})
        }
      ]
    },
    {
      name: 'PeerReview',
      path: '/student/review/:reviewId',
      component: PeerReview,
      beforeEnter: authenticatedStudentsOnly,
      props: route => ({reviewId: route.params.reviewId})
    }
  ]
});

export default router;
