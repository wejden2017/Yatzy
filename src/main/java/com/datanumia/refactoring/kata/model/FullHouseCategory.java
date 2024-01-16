package com.datanumia.refactoring.kata.model;

/**
 * @author wejden
 *
 */
public class FullHouseCategory implements Category {

	@Override
	public int getScore(DiceRoll diceRoll) {
		if (diceRoll.isFullHouse()) {
			return diceRoll.sum();
		}
		return 0;}

}
