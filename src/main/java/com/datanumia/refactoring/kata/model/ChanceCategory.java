package com.datanumia.refactoring.kata.model;

/**
 * @author wejden
 *
 */
public class ChanceCategory  implements Category{

	@Override
	public int getScore(DiceRoll diceRoll) {
		
		return diceRoll.sum();

	}
}
