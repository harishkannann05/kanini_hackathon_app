import React from 'react';
import { IonApp, setupIonicReact } from '@ionic/react';
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import Navbar from './components/Navbar';
import LandingPage from './pages/LandingPage';
import PatientIntake from './pages/PatientIntake';
import Dashboard from './pages/Dashboard';
import Doctors from './pages/Doctors';
import Auth from './pages/Auth';
import AdminDashboard from './pages/AdminDashboard';
import DoctorDashboard from './pages/DoctorDashboard';
import RecipientDashboard from './pages/RecipientDashboard';
import PatientDashboard from './pages/PatientDashboard';

/* Core CSS required for Ionic components to work properly */
import '@ionic/react/css/core.css';

/* Basic CSS for apps built with Ionic */
import '@ionic/react/css/normalize.css';
import '@ionic/react/css/structure.css';
import '@ionic/react/css/typography.css';

/* Optional CSS utils that can be commented out */
import '@ionic/react/css/padding.css';
import '@ionic/react/css/float-elements.css';
import '@ionic/react/css/text-alignment.css';
import '@ionic/react/css/text-transformation.css';
import '@ionic/react/css/flex-utils.css';
import '@ionic/react/css/display.css';

/* Theme variables */
import './index.css';
import './App.css';

setupIonicReact();

// Private Route Component
const PrivateRoute: React.FC<{ component: React.ComponentType<any>; path: string; exact?: boolean }> = ({ component: Component, ...rest }) => {
  const token = localStorage.getItem('token');
  return (
    <Route
      {...rest}
      render={props =>
        token ? (
          <Component {...props} />
        ) : (
          <Redirect to="/login" />
        )
      }
    />
  );
};

const App: React.FC = () => {
  return (
    <IonApp>
      <Router>
        <div className="app-container">
          <Navbar />
          <main className="main-content">
            <Switch>
              <Route exact path="/" component={LandingPage} />
              <Route exact path="/login" component={Auth} />
              <Route exact path="/intake" component={PatientIntake} />
              <Route exact path="/doctors" component={Doctors} />

              {/* Protected Routes */}
              <PrivateRoute exact path="/dashboard" component={Dashboard} />
              <PrivateRoute exact path="/admin-dashboard" component={AdminDashboard} />
              <PrivateRoute exact path="/doctor-dashboard" component={DoctorDashboard} />
              <PrivateRoute exact path="/recipient-dashboard" component={RecipientDashboard} />
              <PrivateRoute exact path="/patient-dashboard" component={PatientDashboard} />

              {/* Fallback */}
              <Redirect from="*" to="/" />
            </Switch>
          </main>
        </div>
      </Router>
    </IonApp>
  );
};

export default App;
