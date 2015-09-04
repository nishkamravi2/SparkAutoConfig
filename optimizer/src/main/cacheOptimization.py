import re
import optimizations as op

<<<<<<< HEAD
#http://stackoverflow.com/questions/241327/python-snippet-to-remove-c-and-c-comments
def commentRemover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " " # note: a space and not an empty string
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE | re.X
    )
    return re.sub(pattern, replacer, text)
    
def getBodyIndex(indexes, application_code):
=======
def getLoopBodyIndex(indexes, application_code):
	"""
	Get loop body indexes from the application code 
	"""
>>>>>>> master
	body_indexes = []
	last_closing_index = -1 #this is to take care of nested loops to prevent overlapping analysis
	for i in range(len(indexes)):
		start_index = indexes[i][0]
		if last_closing_index > start_index: #this is to take care of nested loops to prevent overlapping analysis
			continue
		end_index = -1
		stack = []
		for j in range(start_index,len(application_code)):
			curr_char = application_code[j]
			if curr_char == "{":
				stack.append(curr_char)
				if start_index == indexes[i][0]: #re-initialize start index
					start_index = j
			elif curr_char == "}":
				stack.pop()	 #error check for incorrect open close brackets
				if (len(stack)==0):
					end_index = j+1
					last_closing_index = end_index #this is to take care of nested loops to prevent overlapping analysis
					break;
		#error check for invalid open close (with end index)
		body_indexes.append((start_index,end_index))
	return body_indexes

def getLoopPatternIndex(loop_patterns, application_code):
	loop_keyword_indexes = []
	for keyword in loop_patterns:
		matched = re.finditer(keyword, application_code, re.S)
		loop_keyword_indexes += [m.span() for m in matched]
	return loop_keyword_indexes

def getBodyCodeList(loop_body_indexes, application_code):
	return [application_code[index[0]:index[1]] for index in loop_body_indexes]

def findRDDInBody(body, pattern_list, application_code):
	comments_span_list = op.findCommentSpans(body)
	cache_candidates = set()
<<<<<<< HEAD
	matched = re.finditer(r'(%s)[.\)]' %pattern_list, body, re.MULTILINE) #only find RDDs that will have actions
	if matched:
		for matched_obj in matched:
=======
	matched_iter = re.finditer(r'(%s)\s*[.\)]' %pattern_list, body, re.MULTILINE) #only find RDDs that will have actions
	if matched_iter:
		for matched_obj in matched_iter:
			if op.inComment(matched_obj, body):
				continue
>>>>>>> master
			cache_candidates.add(matched_obj.group(1))
	return cache_candidates

def getRDDOutsideLoops(rdd_set, body_code_list, rdd_patterns):
	for body in body_code_list:
		body_rdd_set = op.findAllRDDs(body, rdd_patterns)
		rdd_set = rdd_set - body_rdd_set
	return rdd_set

def findReassignedRDD(body, pattern_list, comments_span_list, application_code):
	reassigned_candidates = set()
<<<<<<< HEAD
	matched = re.finditer(r'.*(%s)\s+=\s+\w+' %pattern_list, body, re.S)
	if matched:
		for matched_obj in matched:
=======
	matched_iter = re.finditer(r'.*(%s)\s+=\s+\w+' %pattern_list, body, re.S)
	if matched_iter:
		for matched_obj in matched_iter:
			if op.inComment(matched_obj, body):
				continue
>>>>>>> master
			reassigned_candidates.add(matched_obj.group(1))
	return reassigned_candidates

def findFirstLoopIndex(loop_patterns, application_code):
	loop_keyword_indexes = []
	f = application_code.split("\n")
	first_loop_line_num = len(f) + 1
	for keyword in loop_patterns:
		for i in range(0,len(f)):
			matched = re.search(keyword, f[i], re.S)
			if matched:
				if op.inComment(matched, f[i]):
					continue
				if i < first_loop_line_num:
					first_loop_line_num = i 
	return first_loop_line_num + 1

def generateSpaceBuffer(length):
	"""
	Generates space buffer for inserting rdd.cache() neatly
	""" 
	space_buffer = ""
	for i in range(length):
		space_buffer += " "
	return space_buffer

def generateCachedCode(cache_candidates, prev_line):
	"""
	Generates cached code and outputs cache flag given rdd cache cache_candidates
	"""
	leading_spaces = len(prev_line.expandtabs(4)) - len(prev_line.expandtabs(4).lstrip())
	cache_inserted_code = ""
	cacheOptFlag = 1
	if len(cache_candidates) == 0:
		cacheOptFlag = 0
		return cache_inserted_code, cacheOptFlag

	for rdd in cache_candidates:
		cached_line = generateSpaceBuffer(leading_spaces) + rdd + ".cache()" + "\n"
		cache_inserted_code += cached_line

	return cache_inserted_code, cacheOptFlag

def getPrevNonEmptyLine(first_loop_line_num, application_code_array):
	"""
	Obtains the line number of the first prescediing non-empty line
	"""
	prev_line_num = first_loop_line_num - 2
	line = application_code_array[prev_line_num]
	while (line is not None and len(line) == 0):
		prev_line_num -= 1
		line = application_code_array[prev_line_num]
	return max(prev_line_num, 0)

def generateApplicationCode (application_code, first_loop_line_num, cache_candidates, optimization_report):
	f = application_code.split("\n")
	if first_loop_line_num >= len(f):
		first_loop_line_num = 0
	prev_line_num = getPrevNonEmptyLine(first_loop_line_num, f)
	generatedCode, cacheOptFlag = generateCachedCode(cache_candidates, f[prev_line_num])

	if cacheOptFlag == 0:
		optimization_report += "No cache optimizations done.\n"
		return application_code, optimization_report

	line_inserted = first_loop_line_num - 1
	optimization_report += "Inserted code block at Line: " + str(line_inserted) + "\n" + generatedCode + "\n"
	f = '\n'.join(f[:first_loop_line_num - 1]) + '\n' + generatedCode + '\n'.join(f[first_loop_line_num - 1:])
	return f, optimization_report

def extractLoopBodies(application_code, loop_patterns):
	
	#sort indexes by starting indexes to prevent overlap
	loop_keyword_indexes = sorted(getLoopPatternIndex(loop_patterns, application_code), key=lambda x: x[0])
	#find all loop body indexes
	loop_body_indexes = getBodyIndex(loop_keyword_indexes,application_code)
	#get all loop body code
	loop_body_list = getBodyCodeList(loop_body_indexes, application_code)
	return loop_body_list

<<<<<<< HEAD
def cacheOptimization(application_code, rdd_actions, rdd_creations):
	optimization_report = "=====================Cache Optimizations========================\n"
	application_code = commentRemover(application_code)
	rdd_patterns = '|'.join(rdd_actions.split("\n") + rdd_creations.split("\n")) 
	loop_patterns = [r'for\s*\(.+?\)\s*\{', r'while\s*\(.+?\)\s*\{', r'do\s*\{.*\}']

	#find all RDDs in the code
	rdd_set = op.findAllRDDs(application_code, rdd_patterns)
	#extract all the loop bodies 
	loop_body_list = extractLoopBodies(application_code, loop_patterns)
	#extract rdds outside loops
	rdd_body_set = getRDDOutsideLoops(rdd_set, loop_body_list, rdd_patterns)
	#create pattern to capture rdds outside
	regex_pattern = "|".join(rdd_body_set)
=======
def getRDDUsedInLoopsSet(loop_body_list, regex_pattern, application_code):
>>>>>>> master
	cache_candidates = set()

	#cache rdd if rdd is instantiated outside && is in loop && is not cached outside the loop
	for body in loop_body_list:
<<<<<<< HEAD
		cache_candidates.update(findRDDInBody(body, regex_pattern))
	#clear those that are getting reassigned.
	for body in loop_body_list:
		cache_candidates.difference_update(findReassignedRDD(body, regex_pattern))
	#filter out those that are cached
=======
		cache_candidates.update(findRDDInBody(body, regex_pattern, application_code))
	return cache_candidates

def removeReassignedRDDs(loop_body_list, regex_pattern, cache_candidates, comments_span_list, application_code):
	for body in loop_body_list:
		cache_candidates.difference_update(findReassignedRDD(body, regex_pattern, comments_span_list, application_code))
	return cache_candidates

def removeCachedRDDs(cache_candidates, application_code):
	comments_span_list = op.findCommentSpans(application_code)
>>>>>>> master
	filtered_cache_candidates = set()

	for rdd in cache_candidates:
		if op.isCached(rdd, comments_span_list, application_code) == False:
			filtered_cache_candidates.add(rdd)
<<<<<<< HEAD
=======
	return filtered_cache_candidates

def cacheOptimization(application_code, rdd_actions, rdd_creations):
	comments_span_list = op.findCommentSpans(application_code)
	optimization_report = "===================== Cache Optimization =============================\n"
	# application_code = removeComments(application_code) 
	rdd_patterns = '|'.join(rdd_actions.split("\n") + rdd_creations.split("\n")) 
	loop_patterns = [r'for\s*\(.+?\)\s*\{', r'while\s*\(.+?\)\s*\{', r'do\s*\{.*\}']
	#extract all the loop bodies 
	loop_body_list = extractLoopBodies(application_code, loop_patterns)
	#extract rdds outside loops
	rdds_instantiated_outside_loops = getRDDOutsideLoops(application_code, loop_body_list, rdd_patterns)
	#create pattern to capture rdds outside
	outside_rdd_pattern = "|".join(rdds_instantiated_outside_loops)
	#get RDDs instantiated outside loops and used in loops
	cache_candidates = getRDDUsedInLoopsSet(loop_body_list, outside_rdd_pattern, application_code)
	#filter that are getting reassigned/written to.
	cache_candidates = removeReassignedRDDs(loop_body_list, outside_rdd_pattern, cache_candidates, comments_span_list, application_code)
	#filter out those that are already cached
	cache_candidates = removeCachedRDDs(cache_candidates, application_code)
>>>>>>> master

	first_loop_linenum = findFirstLoopIndex(loop_patterns, application_code)
	new_application_code, optimization_report = generateApplicationCode(application_code, first_loop_linenum, filtered_cache_candidates, optimization_report)

	return new_application_code, optimization_report

#dependency for many different loops

