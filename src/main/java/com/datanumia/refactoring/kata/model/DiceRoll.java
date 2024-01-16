package com.datanumia.refactoring.kata.model;

import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * @author wejden
 *
 */
public class DiceRoll {
	
    private final List<Integer> dices;

	public DiceRoll(List<Integer> dices) {
		this.dices = dices;
	}

	public List<Integer> getDices() {
		return dices;
	}



	public Map<Integer, Integer> getCountsByDice() {
		return dices.stream().collect(Collectors.groupingBy(Function.identity(), Collectors.summingInt(x -> 1)));
	}

	public boolean isYatzy() {
		return getCountsByDice().values().stream().anyMatch(c -> c == 5);
	}

	public List<Integer> getDiceCountsGreaterThan(int n) {
		return getCountsByDice().entrySet().stream().filter(entry -> entry.getValue() >= n).map(Entry::getKey)
				.collect(Collectors.toList());
	}

	public List<Integer> getPairs() {
		return getDiceCountsGreaterThan(2).stream().sorted(Comparator.reverseOrder()).collect(Collectors.toList());
	}


	public boolean hasThreeOfAKind() {
		return getDiceCountsGreaterThan(3).stream().findAny().orElse(0) != 0;
	}

	public boolean hasAPair() {
		return getDiceCountsGreaterThan(2).stream().findAny().orElse(0) != 0;

	}

	public boolean isFullHouse() {
		return hasThreeOfAKind() && hasAPair() && !isYatzy();
	}

	public int sum() {
		return dices.stream().mapToInt(Integer::intValue).sum();
	}

}
