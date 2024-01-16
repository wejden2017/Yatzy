package com.datanumia.refactoring.kata.model;

/**
 * @author wejden
 *
 */
public class TwoPairCategory implements Category {

	@Override
	public int getScore(DiceRoll diceRoll) {
		if (diceRoll.getPairs().size() >= 2) {
			return diceRoll.getPairs().stream().mapToInt(d -> d * 2).sum();
		}
		return 0;
	}

}
