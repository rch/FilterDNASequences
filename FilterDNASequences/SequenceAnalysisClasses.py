import re 
from collections import namedtuple
import Exceptions
import types
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC
# import SequenceConstantsObject


class SequenceSubstringCheck:
	"""A basic template class to be subclassed, below.
	
	By convention, these class names generally describe a yes-or-no question;
	accordingly, the Ask() method should always return a boolean.
	"""
	def __init__(self):
		self.sRegex = None
		self.oCompiledRegex = None
	def Ask(self, sDNAString):
		pass
	def TestSelf(self):
		pass


class ContainsForwardAndReversePrimers(SequenceSubstringCheck):
	def __init__(self, SequenceConstantsObject):
		self.sRegex = '(.*){}.+{}.*'.format(SequenceConstantsObject.sFORWARD_PRIMER,
			SequenceConstantsObject.sREVERSE_PRIMER)
		self.oCompiledRegex = re.compile(self.sRegex)
	def ReturnSequencePrependingForwardPrimer(self, sCompleteSequence):
		return self.oCompiledRegex.search(sCompleteSequence).group(1)
	def Ask(self, sDNAString):
		return bool(self.oCompiledRegex.search(sDNAString))


class ContainsForwardAndReversePrimers_Complement(SequenceSubstringCheck):
	def __init__(self, SequenceConstantsObject):
		self.sRegex = '(.*){}.+{}(.*)'.format(SequenceConstantsObject.sREVERSE_PRIMER_COMPLEMENT,
			SequenceConstantsObject.sFORWARD_PRIMER_COMPLEMENT,)
		self.oCompiledRegex = re.compile(self.sRegex)
	def ReturnSequenceAppendingForwardPrimer(self, sCompleteSequence):
		return self.oCompiledRegex.search(sCompleteSequence).group(2)
	def Ask(self, sCompleteSequence):
		return bool(self.oCompiledRegex.search(sCompleteSequence))


class IsATissueTag(SequenceSubstringCheck):

	def __init__(self, lTissueTagTupleList):
		self.oCompiledRegex = None
		self.lAllCompleteTags = set([sTuple.tag for sTuple in lTissueTagTupleList])
		self.dAllPossibleSubtags = self.FillOutAllPossibleSubstrings(self.lAllCompleteTags)

	# this is run on class init, but can be run at other times for testing.
	def FillOutAllPossibleSubstrings(self, lTags):
		dAllPossibleSubtags = {}
		for sTag in lTags:
			# Only include subtags down to length 3, because we're not accepting any shorter.
			for iStartPos in range(0, len(sTag) - 2):
				sSubTag = sTag[iStartPos:]
				if sSubTag in dAllPossibleSubtags:
					dAllPossibleSubtags[sSubTag] += 1
				else:
					dAllPossibleSubtags[sSubTag] = 0
		return dAllPossibleSubtags

	def Ask(self, sPossibleTag, bMatchEntireTagOnly=False):
		bIsTissueTag = False
		if bMatchEntireTagOnly:
			if sPossibleTag in self.lAllCompleteTags:
				bIsTissueTag = True
		else:
			# Second condition, below, ensures that we avoid ambiguous positives:
			# 'AT' could have come from both 'GAT' and 'AAT', so don't count it.
			if sPossibleTag in self.dAllPossibleSubtags and self.dAllPossibleSubtags[sPossibleTag] < 1:
				bIsTissueTag = True
		return bIsTissueTag

	# used only for unit testing.
	def GetTagsAndPartialTags(self):
		return {'tags': self.lAllCompleteTags, 'partial_tags': self.dAllPossibleSubtags}

	# used only for unit testing.
	def AddTag(self, sTag):
		self.lAllCompleteTags.add(sTag)
		self.dAllPossibleSubtags = self.FillOutAllPossibleSubstrings(self.lAllCompleteTags)

	# used only for unit testing.
	def ClearAllTags(self):
		self.lAllCompleteTags = []
		self.dAllPossibleSubtags = {}
		


class IsATissueTag_Complement(SequenceSubstringCheck):

	def __init__(self, lTissueTagTupleList):
		self.oCompiledRegex = None
		self.lAllCompleteTags = set([sTuple.tag for sTuple in lTissueTagTupleList])
		self.lAllCompleteTags_Complement = self.GetSetOfComplementTags(self.lAllCompleteTags)
		self.dAllPossibleSubtags = self.FillOutAllPossibleSubstrings(
			self.lAllCompleteTags_Complement)

	def GetSetOfComplementTags(self, oOriginalTagSet):
			# self.sFORWARD_PRIMER_COMPLEMENT = str(Seq(
			#	self.sFORWARD_PRIMER, IUPAC.unambiguous_dna).reverse_complement())
		oComplementTagSet = set()
		for sOriginalTag in oOriginalTagSet:
			sComplementOfTag =  str(Seq(
				sOriginalTag, IUPAC.unambiguous_dna).reverse_complement())
			oComplementTagSet.add(sComplementOfTag)
		return oComplementTagSet

	def FillOutAllPossibleSubstrings(self, lTags):
		""" This function is run on class init, but can be run at other times for testing. 
		In the complement case,
		substrings for 'EXAMPLE' will be ['EXA', 'EXAM', 'EXAMP', 'EXAMPL', 'EXAMPLE'].
		"""
		dAllPossibleSubtags = {}
		for sTag in lTags:
			# Only include subtags down to length 3, because we're not accepting any shorter.
			for iStartPos in range(len(sTag) - 3, len(sTag) + 1):
				sSubTag = sTag[:iStartPos]
				if sSubTag in dAllPossibleSubtags:
					dAllPossibleSubtags[sSubTag] += 1
				else:
					dAllPossibleSubtags[sSubTag] = 0
		return dAllPossibleSubtags

	def Ask(self, sPossibleTag, bMatchEntireTagOnly=False):
		bIsTissueTag = False
		if bMatchEntireTagOnly:
			if sPossibleTag in self.lAllCompleteTags_Complement:
				bIsTissueTag = True
		else:
			# Second condition, below, ensures that we avoid ambiguous positives:
			# 'AT' could have come from both 'GAT' and 'AAT', so don't count it.
			if sPossibleTag in self.dAllPossibleSubtags and self.dAllPossibleSubtags[sPossibleTag] < 1:
				bIsTissueTag = True
		return bIsTissueTag

	# used only for unit testing.
	def GetTagsAndPartialTags(self):
		return {'tags': self.lAllCompleteTags_Complement, 'partial_tags': self.dAllPossibleSubtags}

	# used only for unit testing.
	def AddTag(self, sTag):
		self.lAllCompleteTags_Complement.add(sTag)
		self.dAllPossibleSubtags = self.FillOutAllPossibleSubstrings(self.lAllCompleteTags_Complement)

	# used only for unit testing.
	def ClearAllTags(self):
		self.lAllCompleteTags = []
		self.dAllPossibleSubtags = {}






class ContainsBothFlankingSequences(SequenceSubstringCheck):

	def __init__(self, SequenceConstantsObject):
		self.sRegex = '.+{}(.+){}.+'.format(
			SequenceConstantsObject.sBEGINNING_FLANKING_SEQUENCE, 
			SequenceConstantsObject.sENDING_FLANKING_SEQUENCE)
		self.oCompiledRegex = re.compile(self.sRegex)

	def ReturnInsertSequence(self, sCompleteSequence):
		sInsertSequence = None
		try:
			sInsertSequence = self.oCompiledRegex.search(sCompleteSequence).group(1)
		except AttributeError as e:
			sInsertSequence = 'no insert sequence pattern matched.'
		return sInsertSequence

	# Return None for tuple if flanking sequences are not found.
	def ReturnInsSeqBegEndPos(self, sCompleteSequence):
		tInsSeqBegEndPos = None
		try:
			if self.oCompiledRegex.search(sCompleteSequence):
				tInsSeqBegEndPos = self.oCompiledRegex.search(sCompleteSequence).span(1)
			return tInsSeqBegEndPos
		except AttributeError as e:
			raise	

	def Ask(self, sCompleteSequence):
		return bool(self.oCompiledRegex.search(sCompleteSequence))

class ContainsBothFlankingSequences_Complement(SequenceSubstringCheck):

	def __init__(self, SequenceConstantsObject):
		self.sRegex = '.+{}(.+){}.+'.format(
			SequenceConstantsObject.sENDING_FLANKING_SEQUENCE_COMPLEMENT,
			SequenceConstantsObject.sBEGINNING_FLANKING_SEQUENCE_COMPLEMENT)
		self.oCompiledRegex = re.compile(self.sRegex)

	def ReturnInsertSequence(self, sCompleteSequence):
		sInsertSequence = None
		try:
			sInsertSequence = self.oCompiledRegex.search(sCompleteSequence).group(1)
		except AttributeError as e:
			sInsertSequence = 'no insert sequence pattern matched.'
		return sInsertSequence

	# Return None for tuple if flanking sequences are not found.
	def ReturnInsSeqBegEndPos(self, sCompleteSequence):
		tInsSeqBegEndPos = None
		try:
			if self.oCompiledRegex.search(sCompleteSequence):
				tInsSeqBegEndPos = self.oCompiledRegex.search(sCompleteSequence).span(1)
			return tInsSeqBegEndPos
		except AttributeError as e:
			raise	

	def Ask(self, sCompleteSequence):
		return bool(self.oCompiledRegex.search(sCompleteSequence))


class InsertSequencePassesTests(SequenceSubstringCheck):
	def __init__(self):
		pass
	def Ask(self, sCompleteSequence):
		# Is the length of the string a multiple of 3?
		return (len(sCompleteSequence) % 3 == 0)

class QualiSequenceIsValid(SequenceSubstringCheck):
	def __init__(self):
		pass	
	def QualiSequenceIsValid(self, sQualiSequence):
		# doesn't have any characters besides integers and spaces.
		# doesn't have any doubled spaces.		
		return None
	def Ask(self, sQualiSequence):
		pass


class QualiInsertSequenceAllAboveThreshold(SequenceSubstringCheck):

	def __init__(self):
		pass

	def GetQualiInsertSubsequence(self, sQualiSequence, tInsSeqBegEndPos):
		# QualiSequenceIsValid(sQualiSequence) # look for errors
		sReturnSubsequence = None
		try:
			if isinstance(tInsSeqBegEndPos, types.NoneType):
				sReturnSubsequence = None
			elif isinstance(tInsSeqBegEndPos, tuple):
				sSplitString = [int(sDigits) for sDigits in sQualiSequence.strip().split(' ')]
				sReturnSubsequence = sSplitString[tInsSeqBegEndPos[0]:tInsSeqBegEndPos[1]]		
			else:
				raise AttributeError('tInsSeqBegEndPos is of unexpected type: {}'.format(
					type(tInsSeqBegEndPos)))
		except (AttributeError, ValueError) as e:
			print 'tInsSeqBegEndPos is {}'.format(tInsSeqBegEndPos)
			print 'sQualiSequence is {}'.format(sQualiSequence)
			raise


		return sReturnSubsequence

	def Ask(self, sQualiSequence, tInsSeqBegEndPos):
		sQualiInsertSequence = self.GetQualiInsertSubsequence(sQualiSequence, tInsSeqBegEndPos)
		if sQualiInsertSequence is None:
			return False
		else:
			try:
				for iInteger in sQualiInsertSequence:
					if iInteger < 20:
						return False
				return True
			except TypeError as e:
				print 'sQualiInsertSequence is \'{}\''.format(sQualiInsertSequence)
				raise


