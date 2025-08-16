import './App.css';
import { Counter } from './features/Counter.tsx';
import CharacterCard from './Components/CharacterCard/CharacterCard.tsx';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <Counter></Counter>
        <CharacterCard message={'Персонаж'}></CharacterCard>
      </header>
    </div>
  );
}

export default App;
