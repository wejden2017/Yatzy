package com.datanumia.refactoring.kata.service;

import java.util.List;

import com.datanumia.refactoring.kata.model.CategoryEnum;


/**
 * @author wejden
 *
 */
public interface YatzyService {
	
	public Integer getScore(CategoryEnum category, List<Integer> dices);


}
