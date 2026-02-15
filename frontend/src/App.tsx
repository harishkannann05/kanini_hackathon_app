import { IonApp, IonRouterOutlet } from '@ionic/react';
import { IonReactRouter } from '@ionic/react-router';
import { Route, Redirect } from 'react-router-dom';
import PatientIntake from './pages/PatientIntake';
import AdminDashboard from './pages/AdminDashboard';
import DoctorDashboard from './pages/DoctorDashboard';
import RecipientDashboard from './pages/RecipientDashboard';
import PatientDashboard from './pages/PatientDashboard';
import Auth from './pages/Auth';

const App: React.FC = () => (
  <IonApp>
    <IonReactRouter>
      <IonRouterOutlet>
        <Route path="/login" component={Auth} exact />
        <Route path="/intake" component={PatientIntake} exact />
        <Route path="/admin-dashboard" component={AdminDashboard} exact />
        <Route path="/doctor-dashboard" component={DoctorDashboard} exact />
        <Route path="/recipient-dashboard" component={RecipientDashboard} exact />
        <Route path="/patient-dashboard" component={PatientDashboard} exact />
        <Route path="/" render={() => <Redirect to="/login" />} exact />
      </IonRouterOutlet>
    </IonReactRouter>
  </IonApp>
);

export default App;
