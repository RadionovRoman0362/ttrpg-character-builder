import React from "react";

interface CharacterCardProps {
  message: string;
}

const CharacterCard: React.FC<CharacterCardProps> = ({ message }) => {
  return (
    <div>
      <h1>{message}</h1>
      <p>Тестовое описание персонажа</p>
    </div>
  );
};

export default CharacterCard;