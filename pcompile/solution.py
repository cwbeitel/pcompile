#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcompile import ureg

from pcompile.helper import unserialize, serialize, strip_internal, to_pint
import numpy as np

from pcompile.items import max_volume
from math import floor
from copy import copy
from statistics import stdev, mean

class Component(object):

    def __init__(self,
                 name=None,
                 concentration=None,
                 classification=None,
                 attr=None):

        self.name = name
        self.concentration = concentration
        self.classification = classification
        self.attr = attr

        if type(self.concentration) is type(''):
            self.concentration = unserialize(self.concentration)

    def to_dict(self):
        return self.__dict__


class Solution(object):
    '''An object for representing complex mixtures of chemicals.
    '''

    def __init__(self,
                 volume=None,
                 history=None,
                 name=None,
                 components=None,
                 other=None,
                 concentration=None,
                 classification=None,
                 container=None,
                 storage_temp=None,
                 comp_index=None):

        self.volume = volume
        self.history = history
        self.name = name
        self.components = components
        self.other = other
        self.concentration = concentration
        self.classification = classification
        self.container = container
        self.storage_temp = storage_temp
        self.comp_index = comp_index

        if self.volume is None:
            self.volume = 0 * ureg.microliter

        if self.components is None:
            self.components = []

    def update_units(self):
        '''Check that all the concentration, molecule, and volume units
        are pint Quantity objects, and in the case they are strings, as would
        be returned from the database, convert the string to a pint quantity.
        '''

        self.volume = to_pint(self.volume)
        self.concentration = to_pint(self.concentration)

        for i,c in enumerate(self.components):

            if 'concentration' in c:
                self.components[i]['concentration'] = to_pint(c['concentration'])

    def build_component_index(self):

        cindex = {}
        ct = 0

        if len(self.components) > 0:

            for c in self.components:

                if isinstance(c, dict) and 'classification' in c:

                    si = strip_internal(c['classification'])

                    key = serialize(si)
                    if key in cindex:
                        raise Exception('warning, found duplicate components'+\
                        ' in solution object')
                    cindex[key] = ct
                    ct += 1
                else:
                    # If a component does not have a classification, then it is
                    # not indexed. E.g. want to keep a placeholder for something
                    # ambiguous like "stabilizers" but don't yet have a rigorous
                    # classification or concentration for that.
                    pass

            self.comp_index = cindex

        else:
            self.comp_index = {}

    def to_dict(self):
        return self.__dict__

    def compatible(self, solution):

        compatible = True

        assert isinstance(solution, Solution)
        self.build_component_index()

        for c in solution.components:

            if 'concentration' not in c:
                compatible = False
                # Has a matching component of unknown concentration.

            assert isinstance(c['concentration'], ureg.Quantity)
            key = serialize(strip_internal(c['classification']))

            if key in self.comp_index:

                c_target_conc = self.components[self.comp_index[key]]['concentration']
                if c['concentration'].to_base_units().units != c_target_conc.to_base_units().units:
                    compatible = False

        return compatible

    def add(self, solution, volume, hypothetical=False, safety_first=True):
        '''Add a specified volume of a solution to this solution.'''

        #print "=========================="
        #print "== " + traceback.extract_stack()[-2][2] + ' / ' + traceback.extract_stack()[-1][2]
        #print "=========================="


        # Any time solution add is called it should update the histories of
        # both solutions involved, adding a simple dict that specified what
        # operation was performed and some way that, given only one of the
        # solutions, you could reconstruct which chemials were added to the
        # solution, when.

        if safety_first:
            assert isinstance(volume, ureg.Quantity)
            assert isinstance(solution, Solution)

        vtot = self.volume + volume
        if vtot == 0.0 * ureg.microliter:
            return

        #print 'adding ' + str(volume) + ' from'
        #print solution.components
        #import ipdb; ipdb.set_trace()

        # Check that what would be the final volume will be less than the max
        # volume of the well containing the solution to which an addition
        # would be made.
        # Only relevant for soutions that are contained in some container.
        # Allows working with hypothetical solutions that don't have containers
        # as well.
        if not hypothetical:
            if self.container is not None and 'ctype' in self.container:
                assert vtot <= max_volume(self.container['ctype'])

        self.build_component_index()
        solution.build_component_index()

        for c in solution.components:

            if ('classification' in c) and ('concentration' in c):

                if safety_first:
                    assert isinstance(c['concentration'], ureg.Quantity)

                key = serialize(strip_internal(c['classification']))

                if key in self.comp_index:

                    key_target = self.comp_index[key]
                    c_target_conc = self.components[key_target]['concentration']

                    if safety_first:
                        assert c['concentration'].to_base_units().units == c_target_conc.to_base_units().units, \
                        'attempted to add two incompatible soutions, use solution.compatible(other_solution) to '+\
                        'check compatibility before combining'

                    #print 'add: found and adding'

                    conc = volume/vtot * c['concentration'] + self.volume/vtot * c_target_conc
                    self.components[key_target]['concentration'] = conc.to(c['concentration'].units)

                    #print c['concentration'], conc

                else:

                    #print 'add: wasnt in index, appending'

                    #print 'appending:'
                    #print c
                    self.components.append(copy(c))
                    self.comp_index[key] = len(self.comp_index.keys()) - 1
                    #print 'last before update'
                    #print self.components[-1]
                    self.components[-1]['concentration'] = volume/vtot * c['concentration']
                    #print 'looking up just appended'
                    #print self.components[-1]

                if safety_first:
                    assert isinstance(c['concentration'], ureg.Quantity)

        for c in self.components:

            if 'classification' in c:

                key = serialize(strip_internal(c['classification']))

                if key not in solution.comp_index:

                    #print 'add: not found but adding'

                    conc = self.components[self.comp_index[key]]['concentration']
                    self.components[self.comp_index[key]]['concentration'] = self.volume/vtot * conc

        self.volume = vtot

        if not hypothetical:
            solution.remove(volume)
            assert isinstance(self.volume, ureg.Quantity)

        #print 'finished add loop'

    def remove(self, volume):
        '''Update solution model upon removal of volume.'''

        assert isinstance(volume, ureg.Quantity)
        self.volume = self.volume - volume

    def dist(self, another_solution, compare_volumes=True, safety_first=True):
        '''Compute the absolute molarity distance between two solutions, i.e.
        the sum of the absolute difference in the number of moles per unit volume
        present of each chemical.

        For components with '_ignore':True for both in a pair of matching
        components, the concentration difference for these will not be added
        to the total. This is to be used for diluents, such as water, in the
        case that the concentration of water is not relevant.
        '''

        dist = 0

        self.build_component_index()
        another_solution.build_component_index()

        dmax = len(self.comp_index) + len(another_solution.comp_index)

        for c in self.components:

            if ('classification' in c) and isinstance(c, dict):

                key = serialize(strip_internal(c['classification']))

                if key in another_solution.comp_index:

                    ind = another_solution.comp_index[key]

                    if ('concentration' not in c) or ('concentration' not in another_solution.components[ind]):
                        dist += 1
                    else:

                        c1 = c['concentration']
                        c2 = another_solution.components[ind]['concentration']

                        if safety_first:
                            assert c1.to_base_units().units == c2.to_base_units().units

                        mn = min(c1, c2).to_base_units().magnitude
                        mx = max(c1, c2).to_base_units().magnitude
                        if mn == 0:
                            dist += 1
                        elif mx > 0:
                            dist += 1 - mn / mx
                        # otherwise, they are both zero, add nothing to the dist

                else:
                    dist += 1
            else:
                dmax -= 1

        for c in another_solution.components:

            if ('classification' in c) and isinstance(c, dict):

                key = serialize(strip_internal(c['classification']))

                if key not in self.comp_index:

                    if safety_first:
                        assert isinstance(c['concentration'], ureg.Quantity)

                    dist += 1
            else:
                dmax -= 1

        if dmax > 0:
            return dist/dmax
        else:
            # Not sure about this. There are two different uses, that of getting
            # a usable dist and that of testing whether two are equivalent.
            return dist

    def intersection_dist(self, another_solution):

        self.build_component_index()
        another_solution.build_component_index()

        dmax = 0
        dist = 0

        for c in self.components:

            assert isinstance(c['concentration'], ureg.Quantity)
            key = serialize(strip_internal(c['classification']))

            if (('_ignore_concentration' in c) and \
                c['_ignore_concentration'] == False) or \
                ('_ignore_concentration' not in c):

                if key in another_solution.comp_index:

                    dmax += 1
                    ind = another_solution.comp_index[key]

                    c1 = c['concentration']
                    c2 = another_solution.components[ind]['concentration']

                    assert c1.to_base_units().units == c2.to_base_units().units
                    mn = min(c1, c2).to_base_units().magnitude
                    mx = max(c1, c2).to_base_units().magnitude
                    if mn == 0:
                        dist += 1
                    elif mx > 0:
                        dist += 1 - mn / mx

        return dist/dmax

    def dist_self_to_target(self, target_solution, safety_first=True):
        '''using canberra distance for now'''

        #print "=========================="
        #print "== " + traceback.extract_stack()[-2][2] + ' / ' + traceback.extract_stack()[-1][2]
        #print "=========================="

        self.build_component_index()
        target_solution.build_component_index()
        #print target_solution.comp_index
        #print self.comp_index

        dist = 0
        ignore_count = 0

        for c in target_solution.components:

            assert isinstance(c['concentration'], ureg.Quantity)
            key = serialize(strip_internal(c['classification']))

            if (('_ignore_concentration' in c) and \
                c['_ignore_concentration'] == False) or \
                ('_ignore_concentration' not in c):

                c1 = c['concentration']

                if key not in self.comp_index:
                    #print 'problem...'
                    c2 = c1 * 0
                else:
                    ind = self.comp_index[key]
                    c2 = self.components[ind]['concentration']

                if safety_first:
                    assert c1.to_base_units().units == c2.to_base_units().units

                v1 = c1.to_base_units().magnitude
                v2 = c2.to_base_units().magnitude

                denom = float(v1 + v2)
                if denom != 0:
                    dist += abs(v1 - v2) / denom

            else:

                ignore_count += 1

        #print dist / float(len(target_solution.components))
        return dist / float(len(target_solution.components) - ignore_count)

    def update_history(self, entry):
        '''Append an entry to the solution object history'''

        if self.history is None:
            self.history = []

        # For now just this
        self.history.append(entry)

    def ref(self, env, rtype="well"):
        '''Obtain the container ref for the container that contains
        this solution. If it has not yet been created and still needs to be
        reffed based on its location, do so. If one attempts to obtain a ref
        for a solution with a container that has neither already been reffed
        nor has a location ID, an exception will occur.
        '''

        assert self.container is not None

        # If it already has a ref, return it
        if ('well_ref' in self.container) and (rtype is "well"):
            return self.container['well_ref']
        if ('container_ref' in self.container) and (rtype is "container"):
            return self.container['container_ref']

        # Otherwise, the container must already have a location ID and a ctype
        # in order to be reffable.
        assert 'location' in self.container
        assert 'ctype' in self.container and self.container['ctype'] is not None

        if ('well_ref' not in self.container) or (self.container['well_ref'] is None):

            if ('name' not in self.container) or (self.container['name'] is None):

                name = env.items.name_registry.new(self.name)
                self.container['name'] = name

            # For now presuming that every location ID is a transcriptic location
            #print self.container
            #location = self.container['location'].split(':')[0]
            location = self.container['location'].split(':')[0]
            ctype = self.container['ctype']
            ref = env.protocol.ref(self.container['name'], id=location,
                                   cont_type=ctype, storage="ambient")
            self.container['container_ref'] = ref
            self.container['well_ref'] = ref.well(0) # Temporary, needs to be
            # more general.

        # -----------------

        # By this point, a ref should have been created and assigned.
        assert 'well_ref' in self.container and self.container['well_ref'] is not None

        if 'parent_index' in self.container:
            index = container['parent_index']
        else:
            index = 0

        if rtype is "well":
            ret = self.container['container_ref'].well(index)
        elif rtype is "container":
            ret = self.container['container_ref']

        return ret


def objective_function(volume_vector, solution_set, target, current_iter, debug=False):#rand_weights, bnds, debug=False):
    '''Score a particular choice of volumes to be taken from a set
    of solutions, whose component concentrations are represented in M,
    toward acheiving a component concentration target as expressed in T.

    Properties of the score:
    - The overall score falls in the range [0,1], with 0 being the best.
    - Each factor score f_i (in [0,1]) is given a weight w_i.
    - The total score is the sum of weighted factors, sum(f_i*w_i), divided
        by the sum of the weights.

    # TODO - make sure the scores are set up to have their best score be
        at 0 and range 0,1

    By simulating the solution each time, it allows you to ask any question
    you want about the properties of the solution.

    By giving each solution a random weight and multiplying these by each
    volume, we create a situation where each solution in an equivalence class
    of solutions has a leader. Then by giving the solution count score itself
    the lowest weight of all factors in the objective function, the optimization
    will first find a combination of volumes to meet concentration and other
    targets, then will concentrate the volume distributed across equivalent
    solutions into as few of these as possible, with priority given to the
    leaders.
    '''

    #print "=========================="
    #print "== " + traceback.extract_stack()[-2][2] + ' / ' + traceback.extract_stack()[-1][2]
    #print "=========================="

    #vv_sum = sum(volume_vector)
    current_iter += 1

    if debug:
        print "---------------------"
        print "scoring iteration " + str(current_iter)
        print solution_set[-1].name
        print volume_vector
        print sum(volume_vector)

    #for v, b in zip(volume_vector, bnds):
    #    print v
    #    print b
        #assert (v >= b[0]) and (v <= b[1])

    #weight_sum = 0
    score = 0.0
    target_volume = target.volume.to("microliter").magnitude

    # Trying to debug something that looks like writing to volume vector
    # during iterations...
    #volume_vector_safe = copy(volume_vector)
    #volume_vector_safe = volume_vector

    # COMPONENT CONCENTRATION SIMILARITY
    w_solution_similarity = 20
    solution = Solution(volume=0.0*ureg.microliter)
    for s, v in zip(solution_set, volume_vector):
        solution.add(s, v*ureg.microliter, hypothetical=True, safety_first=False)

    d = solution.dist_self_to_target(target, safety_first=False)
    weighted_d = d * w_solution_similarity
    print 'conc sim'
    print weighted_d

    #if debug:
    #    print weighted_d

    #print 'components of solution before dist'
    #print solution.components
    #score += solution.dist(target) * w_solution_similarity
    score += weighted_d
    #print 'score'
    #print score
    #weight_sum += w_solution_similarity


    # VOLUME SIMILARITY
    w_vol_sim_score = 500
    vol_sim_score = abs(sum(volume_vector) - target_volume)/abs(sum(volume_vector) + target_volume)
    vss = w_vol_sim_score*vol_sim_score
    if debug:
        print 'vol sim score'
        print vss
    score += vss
    #weight_sum += w_vol_sim_score


    # NUMBER OF SOLUTIONS USED
    # This does not work unless it has a lower weight than other factors.
    # Must be large enough for differences between iterations to be
    # detectable.
    # Dividing by target volume standardizes volume vector elements to [0,1]
    # Highest possible score is 1*max(rand_weights) <= 1
    # Lowest, only for breaking ties.
    '''
    w_solution_count = 100
    solution_count_score = 0
    solution_count_score = mean(volume_vector)/stdev(volume_vector)
    #for a,b in zip(rand_weights, volume_vector/target_volume):
    #    solution_count_score += a * b
    #solution_count_score = solution_count_score
    if debug:
        print "num solution score"
        print solution_count_score * w_solution_count
    score += solution_count_score * w_solution_count
    #weight_sum += w_solution_count
    '''

    # Does this score go down as better solutions are proposed?


    # Don't need to divide by the weight sum unless the weights need to sum
    # to 1.

    #score = score

    return score
    #return abs(score) # DEV


def objective_function_fast(volume_vector, target_volume, molec_matrix, cost_vec, ph_vec, molec_vec_target, debug=False):#rand_weights, bnds, debug=False):
    '''
    '''
    score = 0.0

    # COMPONENT CONCENTRATION SIMILARITY
    w_csim = 1
    csim = abs(volume_vector*molec_matrix - molec_vec_target)

    # VOLUME SIMILARITY
    w_vsim = 1
    vvsum = sum(volume_vector)
    vsim = abs(vvsum - target_volume)/abs(vvsum + target_volume)

    # NUMBER OF SOLUTIONS USED
    w_ct = 1
    ct = stdev(volume_vector)/mean(volume_vector)

    return w_csim*csim + w_vsim*vsim + w_ct*ct


def walloc(env, solution):

    #print 'calling walloc'

    from pcompile.items import min_container_type

    # Allocate a null solution
    s = Solution()

    # Determine the minimum container type
    ctype = min_container_type(solution.volume)

    # Query the "stack" for the next available item of that type.
    container = env.items.allocate(env, ctype)

    s.container = container

    return s


def print_status(x, f, accepted):
    print("at minima %.4f accepted %d with vector %s" % (f, int(accepted), ''.join(str(x))))

class MyBounds(object):
    def __init__(self, xmax, xmin):
        self.xmax = np.array(xmax)
        self.xmin = np.array(xmin)
    def __call__(self, **kwargs):
        x = kwargs["x_new"]
        tmax = bool(np.all(x <= self.xmax))
        tmin = bool(np.all(x >= self.xmin))
        return tmax and tmin

def cluster(v):
    for i in range(len(v)):
        for j in range(len(v)):
            if i != j:
                vi = set(v[i])
                vj = set(v[j])
                if len(vi.intersection(vj)) > 0:
                    v[i] = np.array(list(vi.union(vj)))
                    v = np.delete(v, j, 0)
                    return cluster(v)
    return v

class SolutionPlan(object):

    def __init__(self,
                 target_solution=None,
                 solutions=[],
                 clustering=[]):

        self.target_solution = target_solution
        #self.target_well = target_well
        self.solutions=solutions
        self.clustering=clustering

        # This is a dict of solutions. Keys must be unique to each separate
        # physical entity (solution).
        self.best_result = {'score':0, 'solutions':[]}

        # Check that the object has been initialized propperly.
        for thing in ['target_solution']:#['target_well', 'target_solution']:
            assert getattr(self, thing) is not None, 'Impropperly parameterized'+\
            'solution plan object.'

    def to_dict(self):
        return self.__dict__

    def map_input(self, update, reference):

        # Map solution to the key 'name' in the *target* solution model

        hit = None

        for i,comp in enumerate(self.target_solution.components):

            if comp['_reference'] == reference:

                for key in strip_internal(update):

                    self.target_solution.components[i][key] = update[key]

                hit = 1

        assert hit is not None, 'Couldnt map input.'

    def load_relevant(self, db):

        # Future: Throw out those that don't satisfy binary constraints.
        self.solutions = db.find_solution_set(self.target_solution.components)

    def load_sample(self, db, sample):

        loc = sample['container']['location']

        hits = list(db.db.find({'container.location': loc}))
        if len(hits) > 1:
            print 'Found more than one DB entry for location query.'
            print 'Theres probably something wrong with your database.'
        hit = hits[0]

        stripped = strip_internal(hit)
        s = Solution(**stripped)
        s.update_units() # Note - this will fail if the thing being passed in
        # has a dna concentration of unknown or string None...
        self.solutions.append(s)

    def cluster_solutionset(self):

        m = np.zeros((len(self.solutions),len(self.solutions)))

        for i, s1 in enumerate(self.solutions):
            #print s1.components
            for j, s2 in enumerate(self.solutions):
                print 'comparing components: '
                print s1.components
                print s2
                d = s1.dist(s2)
                #print 'got dist: ' + str(d)
                #if (d == 0) or (i == j):
                #    m[(i,j)] = 1 #np.random.random() # DEV
                if s1.components == s2.components:
                    m[(i,j)] = 1

        #print m

        membership = np.array([-1 for i in m[0]])
        v = []
        for i in range(len(m[0])):
            row = []
            for j in range(len(m[0])):
                if m[(i,j)] > 0:
                    row.append(j)
            v.append(row)
        v = np.array(v)

        r = cluster(v)

        # Translate the clustering into a membership vector
        for i, cl in enumerate(r):
            for j in cl:
                membership[j] = i

        # Use membership vector to construct vector of solution representatives
        reps = []
        repsind = 0

        # At the same time as pulling representatives, put the original solutions
        # into groups that can be used when later translating back from volumes
        # solved for representatives to ones that are divided over the actual
        # solutions
       # sset_grouping = []

        for i in set(membership):

            # Get the indices of all the solutions in this cluster
            ind = np.where(membership == i)
            solutions_this_cluster = copy(np.array(self.solutions)[ind])

            # Append the actual original solutions, not copies of them
            #sset_grouping.append(np.array(self.solutions)[ind])

            for j,s in enumerate(solutions_this_cluster):
                if j == 0:
                    # Initialize a representative using the index of the first solution
                    reps.append(solutions_this_cluster[0])
                else:
                    # If there are more than 1 solutions in the cluster
                    # Simulate adding all identical solutions together
                    reps[repsind].add(s, s.volume, hypothetical=True)

            repsind += 1

        print membership


        #self.clustering = sset_grouping
        self.clustering = membership

        return reps


    def solve(self):

        # Looks like things coming in are in string form and need to be
        # converted to pint before they can be used.

        assert self.target_solution.volume > 0 * ureg.microliter

        # Provide sensical bounds and initial conditions
        bnds = []
        #brutebnds = []
        volumes = []
        # The max volume that any one solution would ever be given the max
        # target volume (provided we're not doing a secondary dilution).
        mx = self.target_solution.volume
        #print self.solutions
        xmx = []
        xmn = []

        # DEV - group by similarity
        solutions = self.cluster_solutionset()
        # -------------

        for s in solutions:

            if not hasattr(s, 'volume'):
                raise AttributeError('A solution was included in a solution'+\
                ' set that did not have a volume attribute.')

            this_mx = min(mx,s.volume).to("microliter").magnitude * 0.999
            mn = 0

            xmx.append(this_mx)
            xmn.append(mn)

            bnds.append((mn,this_mx))

            '''
            stepsize = abs(mn-this_mx)/10.0
            if stepsize > 0:
                brutebnds.append(slice(mn, this_mx, stepsize)) # 0.5ul increments
            else:
                brutebnds.append(slice(0, 0))
            '''

            # Initialize at something close
            even_div = (self.target_solution.volume.to("microliter").magnitude / len(solutions))
            initial = min((mn + (this_mx - mn)/2), max(mn, even_div))

            volumes.append(initial)

        mybounds = MyBounds(xmax=xmx, xmin=xmn)

        volume_0 = np.array(volumes, dtype=object)

        #print 'debug: minimization bounds'
        #print bnds

        target_volume = self.target_solution.volume.to("microliter").magnitude

        # Currently minimizing the number of solutions used by giving them all
        # different random costs so within any set of identical elements there will
        # always be a leader.
        # Alternatively could pre-compute which are better or identify sets and pre-
        # determine which are the leaders.
        # This random weight should be weighted less than any other factor so it can
        # *only* come into play when breaking ties.
        rand_weights = np.random.rand(len(solutions))

        # This constraint requires that the proposed volumes sum to the volume
        # target.
        #cons = ({'type': 'eq', 'fun': lambda x:  sum(x) - target_volume})

        current_iter = 0

        minimizer_kwargs = {"method":"L-BFGS-B",
                            "args":(solutions,
                                    self.target_solution, current_iter,
                                    True),
                                    #rand_weights, bnds, True),
                            "bounds":bnds,
                            "options":{
                                       "maxiter":1, # DEV!
                                       "disp":True
                                       },
                            #"tol": 1e2
                            }


        from scipy.optimize import minimize, basinhopping, brute, fmin

        '''
        res = minimize(objective_function,
                       volume_0,
                       args=(solutions,
                             self.target_solution,
                             rand_weights, bnds),
                       bounds=bnds,
                       method="TNC")
                       #constraints=cons)
        '''

        res = basinhopping(objective_function,
                           volume_0,
                           minimizer_kwargs=minimizer_kwargs,
                           niter=10,
                           accept_test=mybounds,
                           callback=print_status)

        '''
        # Need to constrain search space, this crashed.
        res = brute(objective_function,
                    brutebnds,
                    args=(solutions,
                          self.target_solution,
                          rand_weights, bnds),
                    full_output=True,
                    finish=fmin)
        '''

        '''
        # Doesn't seem to handle bounds...
        np.random.seed(777)
        res = minimize(objective_function,
                       volume_0,
                       args=(solutions,
                             self.target_solution,
                             rand_weights, bnds),
                       bounds=bnds,
                       method="Anneal")
        '''

        self.cluster_volumes = res.x
        #print res

        # DEV --
        # Translate volumes solved for solutions to self.solutions using
        # self.clustering, distributing volume over members of each cluster
        # one at a time.

        self.volumes = [0*ureg.microliter for i in self.solutions]

        for i,v in enumerate(self.cluster_volumes):
            v = v * ureg.microliter
            ind = list(np.where(self.clustering == i)[0])
            for j in ind:
                s = self.solutions[j]
                use_vol = min(s.volume, v)
                v = min((v - use_vol), 0.0 * ureg.microliter)
                self.volumes[j] = use_vol.to("microliter")

        # -------

    def compile(self, env):
        '''Given the planned volumes of a solution set, issue the pipette
        commands to the protocol object, contained in the app run env, that
        are necessary to acheive the planned solution.
        '''

        from pcompile.operations import pipette

        # Add the solutions with the largest volumes first to increase
        # pipetting accuracy.
        #srtd = sorted(zip(self.solutions,self.volumes), key=lambda thingy: thingy[1])
        srtd = zip(self.solutions, self.volumes)


        # -----------

        # The first thing that happens when walloc is called is it creates
        # null solution object. Then it attaches to that the minimum container
        # type that will be able to hold the target solution.

        # Next it comes up with a location attribute. For now, it can just
        # use A1 of a new plate. In the future it should be able to ask for
        # plate stack -> next_plate -> next_well and record next_plate/next_well
        # as the location of the container being attached to the null solution.
        # That can be developed starting from allocating a new 1.5mL tube for
        # each new reaction.

        # Lastly, when the allocated solution is passed to pipette, if the
        # container associated with the solution has not been reffed, it will
        # be.

        # ---------

        target_actual = walloc(env, self.target_solution)

        #print 'loading allocated target well'
        assert 'well_ref' in target_actual.container

        #print 'ta container'
        #print target_actual.container

        for s, v in zip(self.solutions, self.volumes):

            if v > 0 * ureg.microliter:

                # Pipette operations occur between two solutions, that each
                # have associated with them containers, not between two
                # wells.
                pipette(env, s, v, target_actual)

        return target_actual


def compile_solution(env, target_solution, sample):
    '''Given a target solution object, determine how to combine all potentially
    relevant solutions to reach that target. Distance to that target is defined
    in objective_function().

    Notes
    -----
    When compile is called, the solution that is created from the plan is
    what is returned. This has a container attribute which points to the
    container that was allocated in the process of building the solution.
    Allocation of containers is hidden from the user and is done
    automatically at compile-time instead of being pre-specified by the
    user.

    '''

    splan = SolutionPlan(target_solution=target_solution)
    splan.load_relevant(env.db)

    #splan.load_sample(env.db, sample)
    splan.solutions.append(sample)

    splan.solve()
    compiled_solution = splan.compile(env)

    return compiled_solution


def compile_solutions(env, target_solution, samples):

    solutions = []

    for s in samples:

        solution = compile_solution(env, target_solution, s)
        solutions.append(solution)

    return solutions









