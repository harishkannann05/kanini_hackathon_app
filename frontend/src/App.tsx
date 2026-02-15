import React from 'react';
import { IonApp, setupIonicReact } from '@ionic/react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Navbar from './components/Navbar';
import LandingPage from './pages/LandingPage';
import PatientIntake from './pages/PatientIntake';
import Dashboard from './pages/Dashboard';
import Doctors from './pages/Doctors';

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

const App: React.FC = () => {
  return (
    <IonApp>
      <Router>
        <div className="app-container">
          <Switch>
            {/* Landing page without navbar */}
            <Route exact path="/" component={LandingPage} />

            {/* All other pages with navbar */}
            <Route path="*">
              <Navbar />
              <main className="main-content">
                <Switch>
                  <Route exact path="/intake" component={PatientIntake} />
                  <Route exact path="/dashboard" component={Dashboard} />
                  <Route exact path="/doctors" component={Doctors} />
                </Switch>
              </main>
            </Route>
          </Switch>
        </div>
      </Router>
    </IonApp>
  );
};

export default App;
