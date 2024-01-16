package com.datanumia.refactoring.kata.service;

import java.util.List;

import com.datanumia.refactoring.kata.model.CategoryEnum;
import com.datanumia.refactoring.kata.model.DiceRoll;


/**
 * @author wejden
 *
 */
public class YatzyServiceImpl implements YatzyService {

	  @Override
	    public Integer getScore(CategoryEnum category, List<Integer> dices) {
	        if (category == null || dices == null) {
	            throw new IllegalArgumentException("Category and dices can not be null.");
	        }

	        try {
	        	  return CategoriesFactory.buildCategory(category)
	                      .map(cat -> cat.getScore(new DiceRoll(dices)))
	                      .orElse(null);

	        } catch (Exception e) {
	            e.printStackTrace(); 
	            return null;
	        }
	    }

}
