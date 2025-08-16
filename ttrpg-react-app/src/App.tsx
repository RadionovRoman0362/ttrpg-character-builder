import logo from './logo.svg';
import './App.css';
import { Counter } from './features/Counter';
import CharacterCard from './Components/CharacterCard/CharacterCard';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <Counter></Counter>
        <CharacterCard message={'Персонаж'}></CharacterCard>
      </header>
    </div>
  );
}

export default App;
