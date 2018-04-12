import Vue from 'vue';
import Router from 'vue-router';

import {redirectToRoleDashboard, authenticatedInstructorsOnly, authenticatedStudentsOnly} from './guards';
import StudentList from '@/components/StudentList';
import Error from '@/components/Error';
import InstructorDashboard from '@/components/InstructorDashboard';
import StudentDashboard from '@/components/StudentDashboard';
import Modal from '@/components/Modal';
import ReviewsGiven from '@/components/ReviewsGiven';
import ReviewsReceived from '@/components/ReviewsReceived';

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
      props: {errorMessage: 'You do not have permission to visit that page. Please try logging in again.'}
    },
    {
      path: '/instructor/dashboard',
      component: InstructorDashboard,
      beforeEnter: authenticatedInstructorsOnly,
      meta: {
        breadcrumbPathComponents: [{text: 'Peer Review', href: '/instructor/dashboard'}]
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
      path: '/student/dashboard',
      component: StudentDashboard,
      beforeEnter: authenticatedStudentsOnly,
      children: [
        {
          path: 'student/:studentId/reviews/:rubricId/given/',
          name: 'ReviewsGiven',
          component: Modal,
          props: (route) => ({component: ReviewsGiven, childProps: route.params})
        },
        {
          path: 'student/:studentId/reviews/:rubricId/received/',
          name: 'ReviewsReceived',
          component: Modal,
          props: (route) => ({component: ReviewsReceived, childProps: route.params})
        }
      ]
    }
  ]
});

export default router;
