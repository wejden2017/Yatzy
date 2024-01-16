package com.datanumia.refactoring.kata.model;

/**
 * @author wejden
 *
 */
public class TotalValueCategory implements Category {

	private Integer dice;

	public TotalValueCategory(Integer dice) {
		this.dice = dice;
	}

	@Override
	public int getScore(DiceRoll diceRoll) {
		return diceRoll.getCountsByDice().getOrDefault(dice, 0) * dice;
	}

}
