package com.datanumia.refactoring.kata.model;

/**
 * @author wejden
 *
 */
public abstract class StraightCategory implements Category {
   
	private final int score;

    public StraightCategory(int score) {
        this.score = score;
    }

    @Override
    public int getScore(DiceRoll diceRoll) {
        if (isStraight(diceRoll)) {
            return score;
        }
        return 0;
    }

    protected abstract boolean isStraight(DiceRoll diceRoll);
}
