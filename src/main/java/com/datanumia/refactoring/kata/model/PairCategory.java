package com.datanumia.refactoring.kata.model;

/**
 * @author wejden
 *
 */
public class PairCategory implements Category {

	@Override
	public int getScore(DiceRoll diceRoll) {
		if (diceRoll.getPairs().isEmpty()) {
			return 0;
		} else {
			return diceRoll.getPairs().get(0) * 2;
		}
	}

}
