package com.datanumia.refactoring.kata.model;

/**
 * @author wejden
 *
 */
public class YatzyCategory implements Category {

	@Override
	public int getScore(DiceRoll diceRoll) {
		if (diceRoll.isYatzy()) {
			return YatzyConstants.YATZY_SCORE.getValue();

		}
		return 0;
	}

}
