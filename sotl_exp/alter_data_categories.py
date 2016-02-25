#import string as str
import sys

datafile = "data_copy_original.txt"
outfile = "data_copy_new.txt"


####NOTE: Make sure categories are distinct between innovations, impacts, and evaluations
#otherwise sankey will crash

#changes made from original :  added consistency with use of (e.g., ...) and created short version of name for each.

replacementShortEva = {
					#EVALUATION
					"Knowledge tests, diagnostics" : "Knowledge tests",
					"Surveys about perception, attitudes and motivation" : "Attitude surveys",
					"Interviews and focus groups" : "Interviews and focus groups",
					"Observations: open ended ethnographic" : "Observations",
					"Obeservations with protocol rubric" : "Observations",
					"Participant documentation, reflective writing" : "Reflective writing",
					"Existing/secondary data" : "Secondary data",
					"Participant documentation: logging" : "Other Evaluation",
					"Other" : "Other evaluation",
}

replacementsLongInnov = {
					#INNOVATION
					"In-class group work (e.g., small group discussions, group presentations, worksheets)" : "Active Learning - short activities (one or more single-session activities, e.g., clickers)",
					"Other in-class active learning (e.g., clickers, games)" : "Active Learning - short activities (one or more single-session activities, e.g., clickers)",
					"Other out-of-class active learning (e.g., virtual labs)" : "Active Learning - short activities (one or more single-session activities, e.g., clickers)",
					"Out-of-class group work (e.g., projects)" : "Active Learning - multi-session activities (e.g., capstone projects)",
					"PBL/case studies" : "Active Learning - multi-session activities (e.g., capstone projects)",
					"Online discussion/forums" : "Assessment - peer feedback (e.g., PeerWise, Calibrated Peer Review)",
					"Peer assessment/feedback (e.g., paper essays, PeerWise)" : "Assessment - peer feedback (e.g., PeerWise, Calibrated Peer Review)",
					"Student generated content (e.g., wikis)" : "Content - student generated (e.g., wiki, seminar)",
					"Community based/service learning" : "Community based (e.g., community service)",
					"Out of class content delivery (e.g., videos, textbook)" : "Content - instructor generated (e.g., videos)",
					"In-class content delivery (e.g., demos)" : "Content - instructor generated (e.g., videos)",
					"Other assessment (e.g., two-stage exam)" : "Assessment - other (e.g., two-stage exams, diagnostics)",
					"Program level curricular modifications (e.g., learning outcomes alignment)" : "Program Structure (e.g., learning outcomes alignment)",
					"Reduced seat time (e.g., fewer face-to-face contact hours)" : "Reduced seat time (e.g., reducing face-to-face contact hours)",
					#not found "Support for faculty (e.g., professional development)" : "Instructional team enhancement (e.g., roles, support, professional development)",
					"Roles of Teaching Assistants (e.g., adding teaching responsibilities)" : "Instructional Team (e.g., support, professional development, roles)",
					"Technologies development (e.g., annotation systems)" : "Other Innovation",
					"Increase of student choice (e.g., choice of activities, grading)" : "Other Innovation",
					#not found "Strategic support for students (e.g., identifying and supporting at-risk students)" : "Other Innovation"
}

#changes made from original :  added consistency with use of (e.g., ...) and created short version of name for each.
replacementsShortInnov = {
					#INNOVATION
					"In-class group work" : "Active Learning - short activities",
					"Other in-class active learning" : "Active Learning - short activities",
					"Other out-of-class active learning" : "Active Learning - short activities",
					"Out-of-class group work" : "Active Learning - multi-session activities",
					"PBL/case studies" : "Active Learning - multi-session activities",
					"Online discussion/forums" : "Assessment - peer feedback",
					"Peer assessment/feedback" : "Assessment - peer feedback",
					"Student generated content" : "Content - student generated",
					"Community based/service learning" : "Community based",
					"Out of class content delivery" : "Content - instructor generated",
					"In-class content delivery" : "Content - instructor generated",
					"Other assessment" : "Assessment - other",
					"Program level curricular modifications" : "Program Structure",
					"Reduced seat time" : "Reduced seat time",
					#not found "Support for faculty" : "Instructional team enhancement",
					"Roles of Teaching Assistants" : "Instructional teamX",
					"Technologies development" : "Other Innovation",
					"Increase of student choice" : "Other Innovation",
					#not found "Strategic support for students" : "Other Innovation"
}



replacementsLongImpact = {
					#AREA OF IMPACT
					"Course/program specific knowledge (e.g., the French revolution, F=ma)":"Course/program specific knowledge (e.g., the French revolution, F=ma)",
					"Generic Lifelong learning skills (e.g., collaboration, critical/interdisciplinary thinking)":"Professional and Lifelong learning skills (e.g., collaboration, critical/interdisciplinary thinking)",
					"Professional competencies (e.g., appropriate use of procedural/clinical skills)":"Professional and Lifelong learning skills (e.g., collaboration, critical/interdisciplinary thinking)",
					"Attitudes (e.g., perceptions about discipline)":"Attitudes and Motivation (e.g., perceptions about discipline, personal goals)",
					"Motivation (e.g., personal goals)":"Attitudes and Motivation (e.g., perceptions about discipline, personal goals)",
					"Actions and behaviours (e.g.,time on task, enrolment)":"Actions and behaviours (e.g.,time on task, enrolment)",
					"Operations (e.g., finance, reputation)":"Operations (e.g., finance, reputation)",
					"Instructional team (e.g., TA use of time)":"Instructional team Roles and practices(e.g., TA use of time)",
}

replacementsShortImpact = {
					#AREA OF IMPACT
					"Course/program specific knowledge":"Course/program specific knowledge",
					"Generic Lifelong learning skills":"Professional and Lifelong learning skills",
					"Professional competencies":"Professional and Lifelong learning skills",
					"Attitudes":"Attitudes and Motivation",
					"Motivation":"Attitudes and Motivation",
					"Actions and behaviours":"Actions and behaviours",
					"Operations":"Operations",
					"Instructional team":"Instructional team Roles and practice",
}

inputfile = open(datafile,'r')
outputfile = open(outfile, 'w')
countShort = {k : 0 for k in replacementsShortImpact.keys()}
countLong = {k : 0 for k in replacementsLongImpact.keys()}
i=0
for line in inputfile:
	parts = line.split('\t')
	newparts = []
	same_line_impact = False #for old categories where short and long format are the same
	same_line_innov = False #for old categories where short and long format are the same
	for part in parts:
		#Need to do switch impact first because of "Instructional team" category
		if part in replacementsShortImpact.keys() and not same_line_impact:
			newpart = replacementsShortImpact[part]
			countShort[part]+=1
			same_line_impact = True
		elif part in replacementsLongImpact.keys():
			newpart = replacementsLongImpact[part]
			countLong[part]+=1
		elif part in replacementsShortInnov.keys() and not same_line_innov:
			newpart = replacementsShortInnov[part]
			same_line_innov = True 
		elif part in replacementsLongInnov.keys():
			newpart = replacementsLongInnov[part]
		else:
			newpart = part
		newparts.append(newpart)
	outputfile.write('\t'.join(newparts))

for k,v in countLong.iteritems():
	for q in countShort.keys():
		if q in k:
			print v, '\t',k
			print countShort[q], '\t',q
			print "\n"

print "**REMEMBER to make a unique list of rows before rendering!**"
inputfile.close()
outputfile.close












###OLD CATEGORIES

# replacementsShort = {
# 				"In-class group work" : "Single-session active learning",
# 				"Other in-class active learning" : "Single-session active learning",
# 				"Other out-of-class active learning" : "Single-session active learning",
# 				"Out-of-class group work" : "Multi-session active learning",
# 				"PBL/case studies" : "Multi-session active learning",
# 				"Online discussion/forums" : "Peer feedback and interactions",
# 				"Peer assessment/feedback" : "Peer feedback and interactions",
# 				"Student generated content" : "Student generated content",
# 				"Community based/service learning" : "Community based/service learning",
# 				"Out of class content delivery" : "Instructional videos",
# 				"In-class content delivery" : "Non-video Content delivery",
# 				"Other assessment" : "Assessments",
# 				"Program level curricular modifications" : "Program level curricular modifications",
# 				"Reduced seat time" : "Reduced seat time",
# 				"Support for faculty" : "Instructional team",
# 				"Roles of Teaching Assistants" : "Instructional teamX",
# 				"Technologies development" : "Technology development",
# 				"Increase of student choice" : "Other Innovation",
# 				"Strategic support for students" : "Other Innovation"
# 				}

# #changes made from original :  added consistency with use of (e.g., ...) and created short version of name for each.
# replacementsLong = {
# 				"In-class group work (e.g., small group discussions, group presentations, worksheets)" : "Single-session active learning (e.g., clickers, worksheets, simulations)",
# 				"Other in-class active learning (e.g., clickers, games)" : "Single-session active learning (e.g., clickers, worksheets, simulations)",
# 				"Other out-of-class active learning (e.g., virtual labs)" : "Single-session active learning (e.g., clickers, worksheets, simulations)",
# 				"Out-of-class group work (e.g., projects)" : "Multi-session active learning (e.g., PBL, capstone projects, course projects)",
# 				"PBL/case studies" : "Multi-session active learning (e.g., PBL, capstone projects, course projects)",
# 				"Online discussion/forums" : "Peer feedback and interactions (e.g., forums, peer feedback)",
# 				"Peer assessment/feedback (e.g., paper essays, PeerWise)" : "Peer feedback and interactions (e.g., forums, peer feedback)",
# 				"Student generated content (e.g., wikis)" : "Student generated content (e.g., wikis, media)",
# 				"Community based/service learning" : "Community based/service learning",
# 				"Out of class content delivery (e.g., videos, textbook)" : "Instructional videos",
# 				"In-class content delivery (e.g., demos)" : "Non-video Content delivery (e.g., demos, textbook)",
# 				"Other assessment (e.g., two-stage exam)" : "Assessments (e.g., two-stage exam, diagnostics)",
# 				"Program level curricular modifications (e.g., learning outcomes alignment)" : "Program level curricular modifications (e.g., learning outcomes alignment)",
# 				"Reduced seat time (e.g., fewer face-to-face contact hours)" : "Reduced seat time (e.g., fewer face-to-face contact hours)",
# 				"Support for faculty (e.g., professional development)" : "Instructional team (e.g., roles, support, professional development)",
# 				"Roles of Teaching Assistants (e.g., adding teaching responsibilities)" : "Instructional team (e.g., roles, support, professional development)",
# 				"Technologies development (e.g., annotation systems)" : "Technology development (e.g., repositories, annotation systems).",
# 				"Increase of student choice (e.g., choice of activities, grading)" : "Other",
# 				"Strategic support for students (e.g., identifying and supporting at-risk students)" : "Other"
# 				}