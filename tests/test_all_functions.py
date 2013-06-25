#!/usr/bin/env python

"""Calculate the BSR value for all predicted ORFs
in a set of genomes in fasta format.  V3 - replaced
transeq with BioPython.  V4 - changed to true BSR
test.  V5 - fixed bug in how BSR was calculated.
V6 - changed gene caller from Glimmer to Prodigal"""

import unittest
from ls_bsr.util import *
import os
import tempfile
import shutil


curr_dir=os.getcwd()

class Test1(unittest.TestCase):
    def test(self):
        self.assertEqual(get_seq_name("/path/to/test.fasta"), "test.fasta")
    """tests the condition where you use a tilda instead of full path"""
    def test2(self):
        self.assertEqual(get_seq_name("~/test.fasta"), "test.fasta")
    """tests the case where no path is passed"""
    def test3(self):
        self.assertEqual(get_seq_name(""), "")
    """tests the case where something weird is passed"""
    def test4(self):
        self.assertEqual(get_seq_name("\wrong\way"), "\\wrong\\way")
        
class Test2(unittest.TestCase):
    def test(self):
        """tests standard functionality of the translate_consensus function"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile")
        fp = open(fpath, "w")
        fp.write(">Cluster0\n")
        fp.write("ATGACGAGCTTTCCG")
        fp.close()
        self.assertEqual(translate_consensus(fpath), 'MTSFP')
        shutil.rmtree(tdir)
    def test2(self):
        """tests the case of a difference seqeunce.  Also, tests
        wheter a stop codon will be recognized and excluded"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile")
        fp = open(fpath, "w")
        fp.write(">Cluster0\n")
        fp.write("ATGAATCACTACTAA")
        fp.close()
        self.assertEqual(translate_consensus(fpath), 'MNHY')
        shutil.rmtree(tdir)
    def test3(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile")
        fp = open(fpath, "w")
        fp.write(">Cluster1\n")
        """having an integer should make the script throw a typeerror"""
        fp.write("AT1CGAGCTTTCCG")
        fp.close()
        self.assertRaises(TypeError, translate_consensus, fpath)
        shutil.rmtree(tdir)
        os.system("rm tmp.pep")
    def test4(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile")
        fp = open(fpath, "w")
        fp.write(">Cluster1\n")
        fp.write("")
        fp.close()
        self.assertEqual(translate_consensus(fpath), '')
        shutil.rmtree(tdir)
        os.system("rm tmp.pep")
        
class Test3(unittest.TestCase):
    def test(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile")
        fp = open(fpath, "w")
        fp.write(">Cluster0\n")
        """this peptide is 50 AA and should pass through filter"""
        fp.write("LHGRSCRAAFVTFGSTGYFGATAHEPARTTPTNARRRTTANRNACAAPDR\n")
        fp.write(">Cluster1\n")
        """this peptide is 49 AA and should get filtered out"""
        fp.write("LHGRSCRAAFVTFGSTGYFGATAHEPARTTPTNARRRTTANRNACAAPD\n")
        fp.write(">Cluster2\n")
        """empty lines won't throw an error, but will get filtered out"""
        fp.write(" ")
        fp.close()
        self.assertEqual(filter_seqs(fpath),[50])
        os.system("rm consensus.pep")
        shutil.rmtree(tdir)
    def test2(self):
        """tests condition where you have non nucleotide
        characters.  Won't throw an error, but will give
        you an empty set"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile")
        fp = open(fpath, "w")
        fp.write(">Cluster0\n")
        fp.write("12344423432343")
        fp.close()
        self.assertEqual(filter_seqs(fpath),[])
        os.system("rm consensus.pep")
        shutil.rmtree(tdir)
        
class Test4(unittest.TestCase):
    def test(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile")
        fp = open(fpath, "w")
        fp.write("Cluster0	Cluster0	100.00	15	0	0	1	15	1	15	1e-07	30.2\n")
        fp.write("Cluster1	Cluster1	100.00	15	0	0	1	15	1	15	1e-07	40.5\n")
        fp.write("Cluster2	Cluster2	100.00	15	0	0	1	15	1	15	1e-07	60.6")
        fp.close()
        self.assertEqual(parse_self_blast(open(fpath,"U")), {'Cluster2': '60.6', 'Cluster0': '30.2', 'Cluster1': '40.5'})
        shutil.rmtree(tdir)
    def test2(self):
        """tests the condition where too few fields are observed in the blast report.
        should throw an error"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile")
        fp = open(fpath, "w")
        """this file has too few fields"""
        fp.write("Cluster0	Cluster0	100.00	15	0	0	1	15	1	15	1e-07")
        fp.close()
        self.assertRaises(TypeError, parse_self_blast, open(fpath, "U"))
        shutil.rmtree(tdir)
    def test3(self):
        """tests the condition where the file is empty
        should create an empty dictionary"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"empty_file")
        fp = open(fpath, "w")
        fp.write("")
        fp.close()
        self.assertEqual(parse_self_blast(open(fpath,"U")),{})
        shutil.rmtree(tdir)
        
class Test5(unittest.TestCase):
    def test(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile_blast.out")
        os.chdir("%s" % tdir)
        fp = open(fpath, "w")
        fp.write("Cluster0	Cluster0	100.00	15	0	0	1	15	1	15	1e-07	30.2")
        fp.close()
        self.assertEqual(parse_blast_report(), ['Cluster0', '30.2'])
        os.chdir("%s" % curr_dir)
        shutil.rmtree(tdir)
    def test2(self):
        ndir = tempfile.mkdtemp(prefix="filetest_",)
        os.chdir("%s" % ndir)
        fpath = os.path.join(ndir,"output_blast.out")
        fp = open(fpath, "w")
        fp.write("Cluster0	Cluster0	100.00	15	0	0	1	15	1	15")
        fp.close()
        self.assertRaises(TypeError, parse_blast_report)
        os.chdir("%s" % curr_dir)
        shutil.rmtree(ndir)

class Test6(unittest.TestCase):
    def test(self):
        """tests basic functionality of the get_unique_lines function"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered")
        os.chdir("%s" % tdir)
        fp = open(fpath, "w")
        fp.write("Cluster0	30.2\n")
        fp.write("Cluster0	15.3\n")
        fp.close()
        self.assertEqual(get_unique_lines(), ['Cluster0\t30.2\n'])
        os.chdir("%s" % curr_dir)
        shutil.rmtree(tdir)
    def test2(self):
        """if file is empty, you can't get an error
        but you can get an empty set"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered")
        os.chdir("%s" % tdir)
        fp = open(fpath, "w")
        fp.write("")
        fp.close()
        self.assertEqual(get_unique_lines(), [])
        os.chdir("%s" % curr_dir)
        shutil.rmtree(tdir)
    def test3(self):
        """tests condition where you have a different number
        of input fields"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered")
        os.chdir("%s" % tdir)
        fp = open(fpath, "w")
        fp.write("Cluster0	30.2	15.4\n")
        fp.write("Cluster0	15.3\n")
        fp.close()
        self.assertEqual(get_unique_lines(), ['Cluster0\t30.2\t15.4\n'])
        os.chdir("%s" % curr_dir)
        shutil.rmtree(tdir)
        
class Test7(unittest.TestCase):
    def test(self):
        """tests to make sure that list is being populated correctly.  The second file
        is missing a value and the list should be populated with a 0"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.fasta.new_blast.out.filtered.filtered.unique")
        fpath2 = os.path.join(tdir,"testfile2.fasta.new_blast.out.filtered.filtered.unique")
        os.chdir("%s" % tdir)
        fp = open(fpath, "w")
        fp.write("Cluster0	30.2\n")
        fp.write("Cluster1	40.5\n")
        fp.write("Cluster2	60.6")
        fp.close()
        fp2 = open(fpath2, "w")
        fp2.write("Cluster0	15.2\n")
        fp2.write("Cluster2	30.6")
        fp2.close()
        self.assertEqual(make_table(2), (['30.2', '40.5', '60.6', '15.2', 0, '30.6'], ['Cluster0', 'Cluster1', 'Cluster2']))
        os.chdir("%s" % curr_dir)
        shutil.rmtree(tdir)
    def test2(self):
        """tests the case where you have a non float or integer in second field"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.fasta.new_blast.out.filtered.filtered.unique")
        fpath2 = os.path.join(tdir,"testfile2.fasta.new_blast.out.filtered.filtered.unique")
        os.chdir("%s" % tdir)
        fp = open(fpath, "w")
        fp.write("Cluster0	30.2\n")
        fp.write("Cluster1	40.5\n")
        fp.write("Cluster2	60.6")
        fp.close()
        fp2 = open(fpath2, "w")
        fp2.write("Cluster0	15.2\n")
        fp2.write("Cluster1     ABCDE")
        fp2.close()
        self.assertEqual(make_table(2), (['30.2', '40.5', '60.6', '15.2','ABCDE',0], ['Cluster0', 'Cluster1', 'Cluster2']))
        os.chdir("%s" % curr_dir)
        shutil.rmtree(tdir)
    def test3(self):
        """tests the case where you have an empty file"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.fasta.new_blast.out.filtered.filtered.unique")
        fpath2 = os.path.join(tdir,"testfile2.fasta.new_blast.out.filtered.filtered.unique")
        os.chdir("%s" % tdir)
        fp = open(fpath, "w")
        fp.write("Cluster0	30.2\n")
        fp.write("Cluster1	40.5\n")
        fp.write("Cluster2	60.6")
        fp.close()
        fp2 = open(fpath2, "w")
        fp2.close()
        self.assertEqual(make_table(2), (['30.2', '40.5', '60.6', 0, 0, 0], ['Cluster0', 'Cluster1', 'Cluster2']))
        os.chdir("%s" % curr_dir)
        shutil.rmtree(tdir)
        
class Test8(unittest.TestCase):
    def test(self):
        """tests basic functionality of the divide_values function"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered")
        fp = open(fpath, "w")
        fp.write("	sample1	sample2\n")
        fp.write("Cluster0	30.2	15.2\n")
        fp.write("Cluster1	40.5	0\n")
        fp.write("Cluster2	60.6	30.6")
        fp.close()
        self.assertEqual(divide_values(fpath, {'Cluster2': '60.6', 'Cluster0': '30.2', 'Cluster1': '40.5'}),
                     [[1.0, 0.5033112582781457], [1.0, 0.0], [1.0, 0.504950495049505]])
        shutil.rmtree(tdir)
    def test2(self):
        """tests if a condition has a missing value"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered")
        fp = open(fpath, "w")
        fp.write("	sample1	sample2\n")
        fp.write("Cluster0	30.2	15.2\n")
        fp.write("Cluster1	40.5	0\n")
        fp.write("Cluster2	60.6")
        fp.close()
        self.assertRaises(TypeError, divide_values, {'Cluster2': '60.6', 'Cluster0': '30.2', 'Cluster1': '40.5'})
        os.system("rm BSR_matrix_values.txt")
        shutil.rmtree(tdir)
    def test3(self):
        """tests if a non float or integer value is encountered
        should raise an error"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered")
        fp = open(fpath, "w")
        fp.write("	sample1	sample2\n")
        fp.write("Cluster0	30.2	15.2\n")
        fp.write("Cluster1	40.5	ABCDE")
        fp.close()
        self.assertRaises(TypeError, divide_values, {'Cluster2': '60.6', 'Cluster0': '30.2', 'Cluster1': '40.5'})
        shutil.rmtree(tdir)
        
class Test9(unittest.TestCase):
    def test(self):
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered")
        fp = open(fpath, "w")
        fp.write(">gi|22123922|ref|NC_004088.1|_3285\n")
        fp.write("ATGAATCCTCACCTAACCGAACACCCCCCAGTCGGGGATATTGACGCCCTGTTGCAGGACACCTGGCTACAGGTGATCAGCCTGCGTCAAGGGGTAACCTGTGCCGAGGGCGAAGGGCAGGCATTCTGGCAGCGCTGTGTGGCGGACATTGAACGTGTCCATCAGGCGCTGAAAGACGCCGGTCACAGCGAGCAGAGTTGCCAGCACATCCGATACGCCCAATGTGCACTGCTGGATGAG\n")
        fp.write(">gi|22123922|ref|NC_004088.1|_1575\n")
        fp.write("ATGAAGCTAAATATCAAAGTTAATTGTTCTTATATCTGTGAACCCATACGTAAGCAA")
        fp.close()
        """tests to see if the translation is correct, and if shorter sequences
        get filtered out"""
        self.assertEqual(translate_genes(fpath), 'MNPHLTEHPPVGDIDALLQDTWLQVISLRQGVTCAEGEGQAFWQRCVADIERVHQALKDAGHSEQSCQHIRYAQCALLDE')
        os.system("rm genes.pep")
        shutil.rmtree(tdir)
    def test2(self):
        """test the condition where the sequence is not in frame"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered")
        fp = open(fpath, "w")
        fp.write(">gi|22123922|ref|NC_004088.1|_3285\n")
        fp.write("CTCATCCAGCAGTGCACATTGGGCGTATCGGATGTGCTGGCAACTCTGCTCGCTGTGACCGGCGTCTTTCAGCGCCTGATGGACACGTTCAATGTCCGCCACACAGCGCTGCCAGAATGCCTGCCCTTCGCCCTCGGCACAGGTTACCCCTTGACGCAGGCTGATCACCTGTAGCCAGGTGTCCTGCAACAGGGCGTCAATATCCCCGACTGGGGGGTGTTCGGTTAGGTGAGGATTCAT")
        self.assertEqual(translate_genes(fpath), [])
        os.system("rm genes.pep")
        shutil.rmtree(tdir)
    def test3(self):
        """tests the condition where weird characters are encountered"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered")
        fp = open(fpath, "w")
        fp.write(">gi|22123922|ref|NC_004088.1|_3285\n")
        fp.write("1234567890")
        fp.close()
        self.assertRaises(TypeError, translate_genes, fpath)
        os.system("rm genes.pep")
        shutil.rmtree(tdir)
    def test4(self):
        """tests the condition where the file is not fasta.  Will
        not throw an error, but will report an empty set"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered")
        fp = open(fpath, "w")
        fp.write("not a fasta file")
        fp.close()
        self.assertEqual(translate_genes(fpath), [])
        os.system("rm genes.pep")
        shutil.rmtree(tdir)
        
class Test10(unittest.TestCase):
    def test(self):
        """tests standard functionality of rename_fasta_header function"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered")
        fp = open(fpath, "w")
        fp.write(">gi|22123922|ref|NC_004088.1|_3285\n")
        fp.write("ATGCGGGTTGGCCCGGGTTG\n")
        fp.write(">gi|22123922|ref|NC_004088.1|_1575\n")
        fp.write("MNPHLTEHPPVGDIDALLQDTWLQVISLRQGVT")
        fp.close()
        self.assertEqual(rename_fasta_header(fpath, "tmp.out"), ['>centroid_gi|22123922|ref|NC_004088.1|_3285', '>centroid_gi|22123922|ref|NC_004088.1|_1575'])
        os.system("rm tmp.out")
        shutil.rmtree(tdir)
    def test2(self):
        """tests condition where non-normal characters are encountered"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered")
        fp = open(fpath, "w")
        fp.write(">gi|22123922|ref|NC_004088.1|_3285\n")
        fp.write("1234567890")
        fp.close()
        self.assertEqual(rename_fasta_header(fpath, "tmp.out"), ['>centroid_gi|22123922|ref|NC_004088.1|_3285'])
        os.system("rm tmp.out")
        shutil.rmtree(tdir)
    def test3(self):
        """tests condition where the file is not fasta"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered")
        fp = open(fpath, "w")
        fp.write("not a fasta file")
        fp.close()
        self.assertEqual(rename_fasta_header(fpath, "tmp.out"), [])
        os.system("rm tmp.out")
        shutil.rmtree(tdir)

class Test11(unittest.TestCase):
    def test(self):
        self.assertEqual(autoIncrement(), 5)
        
class Test12(unittest.TestCase):
    def test(self):
        """tests the basic functionaly of the prune_matrix function"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"testfile.filtered")
        fp = open(fpath, "w")
        fp.write("        E2348_69_all    H10407_all      O157_H7_sakai_all       SSON_046_all\n")
        fp.write("IpaH3   0.03    0.03    0.03    1.00\n")
        fp.write("LT      0.00    1.00    0.00    0.00\n")
        fp.write("ST1     0.00    1.00    0.12    0.12\n")
        fp.write("bfpB    1.00    0.00    0.00    0.00\n")
        fp.write("stx2a   0.07    0.08    0.98    0.07\n")
        fp.close()
        npath = os.path.join(tdir,"group1")
        np = open(npath, "w")
        np.write("E2348_69_all")
        np.close()
        opath = os.path.join(tdir,"group2")
        op = open(opath, "w")
        op.write("H10407_all")
        op.close()
        self.assertEqual(prune_matrix(fpath,npath,opath), (['E2348_69_all'], ['H10407_all']))
        shutil.rmtree(tdir)
        os.system("rm group*_pruned.txt")
        
class Test13(unittest.TestCase):
    def test(self):
        """test basic functionality of compare_values function"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"group1_pruned")
        fp = open(fpath, "w")
        fp.write("		E2348_69_all\n")
        fp.write("IpaH3 	0.03\n")
        fp.write("LT 	0.00\n")
        fp.write("ST2 	0.00\n")
        fp.write("bfpB 	1.00\n")
        fp.write("stx2a 	0.07")
        fp.close()
        npath = os.path.join(tdir,"group2_pruned")
        np = open(npath, "w")
        np.write("        H10407_all\n")
        np.write("IpaH3   0.03\n")
        np.write("LT      1.00\n")
        np.write("ST2     1.00\n")
        np.write("bfpB    0.00\n")
        np.write("stx2a   0.08")
        np.close()
        self.assertEqual(compare_values(fpath, npath, "0.8", "0.4"), (['1.00'], ['1.00', '1.00']))
        shutil.rmtree(tdir)
    def test2(self):
        """tests the condition where BSR values are near the border regions
        differentiated by the function"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"group1_pruned")
        fp = open(fpath, "w")
        fp.write("		E2348_69_all\n")
        fp.write("IpaH3 	0.03\n")
        fp.write("LT 	0.00\n")
        fp.write("ST2 	0.00\n")
        fp.write("bfpB 	0.81\n")
        fp.write("stx2a 	0.07")
        fp.close()
        npath = os.path.join(tdir,"group2_pruned")
        np = open(npath, "w")
        np.write("        H10407_all\n")
        np.write("IpaH3   0.03\n")
        np.write("LT      0.80\n")
        np.write("ST2     1.00\n")
        np.write("bfpB    0.00\n")
        np.write("stx2a   0.79")
        np.close()
        self.assertEqual(compare_values(fpath, npath, "0.8", "0.4"), (['0.81'], ['0.80', '1.00']))
        shutil.rmtree(tdir)
        os.system("rm group*_out.txt")
        
"""test the mean and average functionalities"""

class Test14(unittest.TestCase):
    def test(self):
        """tests the basic functionality of the find_uniques function"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"combined.txt")
        fp = open(fpath, "w")
        fp.write("IpaH3   0.03    0       1       0       0.03    0       1       0\n")
        fp.write("LT 	0.0 	0 	1 	0	0.8 	1 	1 	1\n")
        fp.write("ST2 	0.0 	0 	1 	0	1.0 	1 	1 	1\n")
        fp.write("bfpB 	0.81 	1 	1 	1	0.0 	0 	1 	0\n")
        fp.write("stx2a 	0.07 	0 	1 	0	0.79 	0 	1 	1")
        fp.close()
        npath = os.path.join(tdir,"fasta")
        np = open(npath, "w")
        np.write(">bfpB\n")
        np.write("ATGAAACTTGGCAGGTATTCACTTTTCTTATTG\n")
        np.write(">LT\n")
        np.write("ATGCCCAGAGGGCATAATGAGTACTTCGA\n")
        np.write("ST2\n")
        np.write("ATGAAGAAATCAATATTATTTATTTTTCTTTCTGTATTGTCTTTT")
        np.close()
        self.assertEqual(find_uniques(fpath, npath), (['bfpB'], ['LT', 'ST2']))
        shutil.rmtree(tdir)
        os.system("rm group*_unique_seqs.fasta")

class Test15(unittest.TestCase):
    def test(self):
        """test the basic functionality of the filter_genomes function"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"sample_matrix.txt")
        fp = open(fpath, "w")
        fp.write("        E2348_69_all    H10407_all      O157_H7_sakai_all       SSON_046_all\n")
        fp.write("IpaH3   0.03    0.03    0.03    1.00\n")
        fp.write("LT      0.00    1.00    0.00    0.00\n")
        fp.write("ST1     0.00    1.00    0.12    0.12\n")
        fp.write("bfpB    1.00    0.00    0.00    0.00\n")
        fp.write("stx2a   0.07    0.08    0.98    0.07\n")
        fp.close()
        npath = os.path.join(tdir,"genomes")
        np = open(npath, "w")
        np.write("H10407_all\n")
        np.write("SSON_046_all")
        np.close()
        """1 and 3 should be the correct indices, based on the input data.  These
        are the genomes that should be removed"""
        self.assertEqual(filter_genomes(npath, fpath), [1, 3])
        shutil.rmtree(tdir)

class Test16(unittest.TestCase):
    def test(self):
        """test the basic functionality of the filter_matrix function"""
        tdir = tempfile.mkdtemp(prefix="filetest_",)
        fpath = os.path.join(tdir,"sample_matrix.txt")
        fp = open(fpath, "w")
        fp.write("        E2348_69_all    H10407_all      O157_H7_sakai_all       SSON_046_all\n")
        fp.write("IpaH3   0.03    0.03    0.03    1.00\n")
        fp.write("LT      0.00    1.00    0.00    0.00\n")
        fp.write("ST1     0.00    1.00    0.12    0.12\n")
        fp.write("bfpB    1.00    0.00    0.00    0.00\n")
        fp.write("stx2a   0.07    0.08    0.98    0.07\n")
        fp.close()
        self.assertEqual(filter_matrix([1, 3], fpath, "test"), [['', 'E2348_69_all', 'O157_H7_sakai_all'],['IpaH3', '0.03', '0.03'],['LT', '0.00', '0.00'],['ST1', '0.00', '0.12'],['bfpB', '1.00', '0.00'],['stx2a', '0.07', '0.98']])
        shutil.rmtree(tdir)
        
if __name__ == "__main__":
    unittest.main()
    main()
