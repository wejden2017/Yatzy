package com.datanumia.refactoring.kata.service;

import java.util.EnumMap;
import java.util.Map;
import java.util.Optional;

import com.datanumia.refactoring.kata.model.Category;
import com.datanumia.refactoring.kata.model.CategoryEnum;
import com.datanumia.refactoring.kata.model.ChanceCategory;
import com.datanumia.refactoring.kata.model.FullHouseCategory;
import com.datanumia.refactoring.kata.model.KindInstanceCategory;
import com.datanumia.refactoring.kata.model.LargeStraightCategory;
import com.datanumia.refactoring.kata.model.PairCategory;
import com.datanumia.refactoring.kata.model.SmallStraightCategory;
import com.datanumia.refactoring.kata.model.TotalValueCategory;
import com.datanumia.refactoring.kata.model.TwoPairCategory;
import com.datanumia.refactoring.kata.model.YatzyCategory;

/**
 * @author wejden
 *
 */
public class CategoriesFactory {
	

    private static Map<CategoryEnum, Category> categories;

    private static void initializeCategories() {
        categories = new EnumMap<>(CategoryEnum.class);
        categories.put(CategoryEnum.CHANCE, new ChanceCategory());
        categories.put(CategoryEnum.YATZY, new YatzyCategory());
        categories.put(CategoryEnum.ONES, new TotalValueCategory(1));
        categories.put(CategoryEnum.TWOS, new TotalValueCategory(2));
        categories.put(CategoryEnum.THREES, new TotalValueCategory(3));
        categories.put(CategoryEnum.FOURS, new TotalValueCategory(4));
        categories.put(CategoryEnum.FIVES, new TotalValueCategory(5));
        categories.put(CategoryEnum.SIXES, new TotalValueCategory(6));
        categories.put(CategoryEnum.PAIR, new PairCategory());
        categories.put(CategoryEnum.TWO_PAIRS, new TwoPairCategory());
        categories.put(CategoryEnum.THREE_OF_KIND, new KindInstanceCategory(3));
        categories.put(CategoryEnum.FOUR_OF_KIND, new KindInstanceCategory(4));
        categories.put(CategoryEnum.SMALL_STRAIGHT, new SmallStraightCategory());
        categories.put(CategoryEnum.LARGE_STRAIGHT, new LargeStraightCategory());
        categories.put(CategoryEnum.FULL_HOUSE, new FullHouseCategory());
    }

    public static Optional<Category> buildCategory(CategoryEnum category) {
        if (categories == null) {
            initializeCategories();
        }
        return Optional.ofNullable(categories.get(category));
    }

}
