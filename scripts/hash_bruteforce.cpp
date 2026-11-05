// Source-guided, exhaustive-within-dictionary Lua 64-bit FNV-1a enumeration.
// Unlike a generic 2^64 preimage attack, this enumerates explicitly documented
// naming grammars constructed from already validated SV and ZA Lua names.
// NEVER changes Hashlists; every match is only H2 candidate until native proof.
// Build: g++ -std=c++20 -O3 -DNDEBUG -pthread scripts/hash_bruteforce.cpp -o hash_bruteforce
// Run: ./hash_bruteforce --repo . --mode sv --out results/sv --budget 300000000
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using std::string;
using std::string_view;
using U64 = std::uint64_t;
constexpr U64 BASIS = 0xCBF29CE484222645ULL;
constexpr U64 PRIME = 0x100000001B3ULL;

U64 extend(U64 h, string_view text) {
    for (unsigned char c : text) h = (h ^ c) * PRIME;
    return h;
}
U64 hashName(string_view text) { return extend(BASIS, text); }
string hex(U64 v) {
    std::ostringstream o;
    o << "0x" << std::uppercase << std::hex << std::setw(16)
      << std::setfill('0') << v;
    return o.str();
}
bool starts(string_view s, string_view x) {return s.size() >= x.size() && s.substr(0,x.size())==x;}
bool ends(string_view s, string_view x) {return s.size() >= x.size() && s.substr(s.size()-x.size())==x;}
bool ident(string_view s) {
    if(s.empty() || s.size()>180) return false;
    for(char ch:s) if(!((ch>='A'&&ch<='Z')||(ch>='a'&&ch<='z')||(ch>='0'&&ch<='9')||ch=='_')) return false;
    return true;
}
string trim(string s) {
    auto p=s.find_first_not_of(" \t\r\n");
    if(p==string::npos)return "";
    auto q=s.find_last_not_of(" \t\r\n");
    return s.substr(p,q-p+1);
}
struct Entry {string game,kind,name;U64 hash;unsigned line;};
struct Leaf {string value,source,rule;};
struct Namespace {string value,source;U64 state;};
struct Hit {string candidate,method,source_a,source_b;U64 target;};
std::vector<Entry> loadAll(const string& repo) {
    std::vector<Entry> rows;
    for(string game:{"SV","ZA"}) for(string kind:{"c","e","f","s"}) {
        string path=repo+"/"+game+"/Hashlists/Lua/lua_"+kind+"_hashes.txt";
        std::ifstream f(path);
        if(!f)throw std::runtime_error("Missing Hashlist: "+path);
        string line;unsigned ln=0;
        while(std::getline(f,line)) {
            ++ln;
            if(trim(line).empty())continue;
            if(line.size()<18||line.substr(0,2)!="0x") throw std::runtime_error("Malformed hash row "+path+":"+std::to_string(ln));
            U64 h=0;
            try {h=std::stoull(line.substr(2,16),nullptr,16);}
            catch(...) {throw std::runtime_error("Bad hash "+path+":"+std::to_string(ln));}
            string name=trim(line.substr(18));
            if(!name.empty()&&hashName(name)!=h)throw std::runtime_error("Preexisting invalid full-hash mapping "+path+":"+std::to_string(ln));
            rows.push_back({game,kind,name,h,ln});
        }
    }
    return rows;
}
struct Search {
    std::unordered_map<U64,std::vector<Entry>> targets;
    std::map<std::pair<U64,string>,Hit> hits;
    std::uint64_t budget=0,attempts=0;
    bool stopped=false;
    string mode;
    explicit Search(const std::vector<Entry>& rows,string mode,std::uint64_t budget):budget(budget),mode(std::move(mode)){
        for(const auto& e:rows) if(e.name.empty() &&
            ((this->mode=="sv" && e.game=="SV" && e.kind=="c") ||
             (this->mode=="za" && e.game=="ZA" && (e.kind=="s"||e.kind=="f"))))
            targets[e.hash].push_back(e);
        if(targets.empty())throw std::runtime_error("No unresolved targets found");
    }
    bool offer(string_view full,string_view rule,string_view src_a,string_view src_b) {
        if(attempts>=budget) {stopped=true;return false;}
        ++attempts;
        U64 h=hashName(full);
        if(auto x=targets.find(h);x!=targets.end())
            hits.try_emplace({h,string(full)},Hit{string(full),string(rule),string(src_a),string(src_b),h});
        return true;
    }
    bool offerPrefixed(const Namespace& ns,const Leaf& leaf) {
        if(attempts>=budget) {stopped=true;return false;}
        ++attempts;
        U64 h=extend(ns.state,leaf.value);
        if(auto x=targets.find(h);x!=targets.end())
            hits.try_emplace({h,ns.value+leaf.value},Hit{ns.value+leaf.value,leaf.rule,ns.source,leaf.source,h});
        return true;
    }
    void report(const string& prefix,const std::vector<std::pair<string,std::uint64_t>>& phases) const {
        std::ofstream hitsFile(prefix+"-matches.tsv");
        hitsFile<<"game\tkind\tline\thash\tcandidate\tmethod\tprefix_source\tleaf_or_stem_source\n";
        for(const auto& [key,hit]:hits) for(const auto& e:targets.at(hit.target))
            hitsFile<<e.game<<'\t'<<e.kind<<'\t'<<e.line<<'\t'<<hex(e.hash)<<'\t'
                <<hit.candidate<<'\t'<<hit.method<<'\t'<<hit.source_a<<'\t'<<hit.source_b<<'\n';
        std::ofstream reportFile(prefix+"-summary.json");
        reportFile<<"{\n \"mode\":\""<<mode<<"\",\n \"hash_algorithm\":\"FNV-1a 64-bit exact UTF-8 bytes\",\n"
                  <<" \"offset_basis\":\"0xCBF29CE484222645\",\n \"target_unknown_hashes\":"<<targets.size()
                  <<",\n \"attempted_candidates\":"<<attempts
                  <<",\n \"max_candidates\":"<<budget
                  <<",\n \"budget_exhausted\":"<<(stopped?"true":"false")
                  <<",\n \"exact_hash_matching_candidates\":"<<hits.size()
                  <<",\n \"native_original_names_confirmed\":0,\n \"hashlist_updates\":0,\n \"phases\":{\n";
        for(size_t i=0;i<phases.size();++i)
            reportFile<<"  \""<<phases[i].first<<"\":"<<phases[i].second<<(i+1<phases.size()?",":"")<<"\n";
        reportFile<<" },\n \"limitations\":\"H2 dictionary-grammar exact hash only; source string identity and runtime type unproven. Missing candidates are not absent symbols.\"\n}\n";
        std::cout<<"mode="<<mode<<" targets="<<targets.size()<<" attempted="<<attempts
                 <<" H2_hits="<<hits.size()<<" budget_exhausted="<<stopped<<"\n";
        for(const auto& [_,hit]:hits)std::cout<<hex(hit.target)<<" "<<hit.candidate<<" ["<<hit.method<<"]\n";
    }
};
void insertLeaf(std::map<string,Leaf>& leaves,string v,string rule,string source) {
    if(v.size()<2||v.size()>180||v.find('\t')!=string::npos)return;
    leaves.try_emplace(v,Leaf{std::move(v),std::move(source),std::move(rule)});
}
std::vector<string> getBaseNames(const std::vector<Entry>& rows) {
    std::set<string> bases;
    const std::vector<string> suffixes={
        "Manager","Controller","Model","Component","System","Handler","Service",
        "Data","State","Info","Table","Accessor","Params","Param","View","Util",
        "Factory","Behavior","Behaviour","Action","Event","Scene","Context",
        "Base","Impl","Object","Type","Command","Script","Sequence","UI","Func","_Impl_"
    };
    for(const auto& e:rows)if(e.kind=="c"&&!e.name.empty()){
        string leaf=e.name.substr(e.name.rfind('.')==string::npos?0:e.name.rfind('.')+1);
        if(!ident(leaf))continue;
        bases.insert(leaf);
        for(const auto& suffix:suffixes)if(ends(leaf,suffix)&&leaf.size()>suffix.size()+3)
            bases.insert(leaf.substr(0,leaf.size()-suffix.size()));
        if(starts(leaf,"I")&&leaf.size()>4&&leaf[1]>='A'&&leaf[1]<='Z')
            bases.insert(leaf.substr(1));
    }
    return {bases.begin(),bases.end()};
}
std::vector<Namespace> namespaces(const std::vector<Entry>& rows) {
    std::map<string,string> ns;
    for(const auto& e:rows)if(e.kind=="c"&&!e.name.empty()) {
        string s=e.name;
        while(true){
            auto p=s.rfind('.');
            if(p==string::npos)break;
            s.resize(p);
            if(!s.empty()&&s.size()<180)ns.try_emplace(s+".",e.name);
        }
    }
    // Top-level Haxe module namespaces in known game assets.
    for(string s:{"main.","event_ik.","dll_util.","main.event.","main.util.","main.ui."})
        ns.try_emplace(s,"documented Lua root namespace");
    std::vector<Namespace> ret;
    for(const auto& [name,source]:ns)ret.push_back({name,source,hashName(name)});
    return ret;
}
void svSearch(Search& search,const std::vector<Entry>& rows,std::vector<std::pair<string,std::uint64_t>>& phases) {
    auto nss=namespaces(rows);
    std::map<string,Leaf> original;
    for(const auto& e:rows)if(e.kind=="c"&&!e.name.empty()){
        auto p=e.name.rfind('.');
        string leaf=e.name.substr(p==string::npos?0:p+1);
        insertLeaf(original,leaf,"source_name_leaf",e.name);
    }
    auto doPhase=[&](const string& label,const std::map<string,Leaf>& leaves){
        U64 before=search.attempts;
        for(const auto& ns:nss)for(const auto& [_,leaf]:leaves)if(!search.offerPrefixed(ns,leaf))goto done;
        done:phases.push_back({label,search.attempts-before});
        std::cout<<"phase "<<label<<" candidates="<<(search.attempts-before)<<" hits="<<search.hits.size()<<"\n";
    };
    doPhase("namespace_x_verified_leaf",original);
    if(search.stopped)return;
    auto bases=getBaseNames(rows);
    std::map<string,Leaf> morph;
    const std::vector<string> suffixes={
        "Manager","Controller","Model","Component","System","Handler","Service",
        "Data","State","Info","Table","Accessor","Params","Param","View","Util",
        "Factory","Behavior","Action","Event","Scene","Context","Base","Impl",
        "Object","Type","Command","Script","Sequence","UI","Func","Status"
    };
    for(const auto& base:bases)if(ident(base)) {
        for(const auto& suf:suffixes)insertLeaf(morph,base+suf,"stem_plus_class_suffix",base);
    }
    doPhase("namespace_x_class_suffix_morph",morph);
    if(search.stopped)return;
    std::map<string,Leaf> nested;
    for(const auto& base:bases)if(ident(base) && base.size()<=80) {
        insertLeaf(nested,"_"+base+"."+base+"_Impl_","haxe_nested_impl_class",base);
        insertLeaf(nested,"_"+base+"."+base,"haxe_nested_class",base);
        insertLeaf(nested,base+"_Impl_","haxe_flat_impl_class",base);
    }
    doPhase("namespace_x_haxe_nested_class",nested);
    if(search.stopped)return;
    std::map<string,Leaf> prep;
    for(const auto& base:bases)if(ident(base)){
        for(string pre:{"I","Base","Common","Default","UI","Event","Field","Battle","Poke","Pokemon","Scene","Game","Data","Sub","General","System","Script","Actor","Player","Network","Field"}) {
            insertLeaf(prep,pre+base,"class_prefix_composition",base);
        }
    }
    doPhase("namespace_x_class_prefix_morph",prep);
}
std::vector<string> camelWords(const string& s) {
    std::vector<string> out;
    string current;
    for(size_t i=0;i<s.size();++i){
        char c=s[i];
        if(!((c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9'))) {
            if(!current.empty()){out.push_back(current);current.clear();}
            continue;
        }
        bool split=!current.empty()&&i>0&&((c>='A'&&c<='Z') &&
            ((s[i-1]>='a'&&s[i-1]<='z') ||
             (i+1<s.size()&&s[i+1]>='a'&&s[i+1]<='z'&&s[i-1]>='A'&&s[i-1]<='Z')));
        if(split){out.push_back(current);current.clear();}
        current+=c;
    }
    if(!current.empty())out.push_back(current);
    return out;
}
void zaSearch(Search& search,const std::vector<Entry>& rows,std::vector<std::pair<string,std::uint64_t>>& phases) {
    const std::vector<string> verbs={
        "Get","Set","Is","Has","Can","Create","Destroy","Delete","Remove","Add",
        "Start","Stop","Begin","End","Open","Close","Load","Unload","Save","Update",
        "Reset","Init","Initialize","Execute","Run","Do","Call","Wait","Check","Request",
        "Enable","Disable","Change","Apply","Clear","Find","Search","Push","Pop",
        "SetUp","Setup","On","on","get_","set_","Wait_","FObj_","Camera_",
        "Play","Show","Hide","Move","Send","Receive","Register","Regist","Unregister",
        "Try","Calc","Calculate","Make","Create_","Set_","Get_","Is_","Play_","Start_",
        "Stop_","Show_","Wait_FObj_","FObj_Set_","FObj_Wait_","FObj_Get_",
        "Check_","get","set","Allow","IsNot","CanNot"
    };
    std::map<string,string> stems;
    std::set<string> words;
    for(const auto& e:rows)if(!e.name.empty()&&(e.kind=="s"||e.kind=="f")){
        if(e.name.size()<=100)stems.try_emplace(e.name,e.name);
        for(const string& verb:verbs)if(starts(e.name,verb)&&e.name.size()>verb.size()+2){
            string tail=e.name.substr(verb.size());
            stems.try_emplace(tail,e.name);
        }
        for(const string& w:camelWords(e.name))if(w.size()>=3&&w.size()<=24)
            words.insert(w);
    }
    for(const auto& e:rows)if(e.kind=="c"&&!e.name.empty()) {
        auto p=e.name.rfind('.');
        string leaf=e.name.substr(p==string::npos?0:p+1);
        if(ident(leaf)&&leaf.size()<=80)stems.try_emplace(leaf,e.name);
        for(const auto& w:camelWords(leaf))if(w.size()>=3&&w.size()<=24)words.insert(w);
    }
    auto check=[&](const string& name,const string& kind,const string& source) {
        return search.offer(name,kind,source,"source-derived grammar");
    };
    U64 start=search.attempts;
    for(const auto& [stem,source]:stems) {
        if(!check(stem,"known_symbol_stem",source))break;
        for(const auto& verb:verbs){
            if(!check(verb+stem,"verb_plus_symbol_stem",source))break;
        }
        if(search.stopped)break;
    }
    phases.push_back({"verb_x_known_symbol_stem",search.attempts-start});
    if(search.stopped)return;
    // Two words from the game-native vocabulary, with a full verb stem.
    // 500 words => about 250k nominal stems and <=20m exact hash checks.
    std::vector<string> ws(words.begin(),words.end());
    // Prefix preference: longer-than-one-letter proper CamelCase source tokens.
    start=search.attempts;
    for(const auto& a:ws)for(const auto& b:ws){
        string noun=a+b;
        if(noun.size()>64)continue;
        for(const auto& v:verbs)
            if(!check(v+noun,"verb_plus_two_native_words",a+"+"+b))goto end_pairs;
    }
    end_pairs:phases.push_back({"verb_x_two_native_camel_words",search.attempts-start});
    if(search.stopped)return;
    // One symbol-derived stem plus one documented noun, to extend actual
    // event/action names without arbitrary full-alphabet enumeration.
    start=search.attempts;
    const std::vector<string> tails={
        "Data","State","Info","Object","Event","Manager","Handler","Flag",
        "Request","Response","Result","Type","Mode","Table","Index","List",
        "Player","Pokemon","Character","Camera","Animation","Effect","Text",
        "UI","Model","Scene","Sequence","Value","Position","Target","Pattern",
        "Script","Battle","Controller","Accessor","Function","Time","Count",
        "Name","Condition","Message","Action","ID","Id","No","Num","Array"
    };
    for(const auto& [stem,source]:stems){
        for(const auto& tail:tails)for(const auto& verb:verbs)
            if(!check(verb+stem+tail,"verb_plus_stem_plus_domain_suffix",source))goto end_tails;
    }
    end_tails:phases.push_back({"verb_x_stem_x_domain_suffix",search.attempts-start});
}
int main(int argc,char** argv) {
    try {
        string repo=".",mode="",out="hash-bruteforce";
        U64 budget=300000000;
        for(int i=1;i<argc;i++){
            string arg=argv[i];
            auto take=[&](){if(i+1>=argc)throw std::runtime_error("Missing value after "+arg);return string(argv[++i]);};
            if(arg=="--repo")repo=take();
            else if(arg=="--mode")mode=take();
            else if(arg=="--out")out=take();
            else if(arg=="--budget")budget=std::stoull(take());
            else throw std::runtime_error("Unknown argument: "+arg);
        }
        if((mode!="sv"&&mode!="za")||budget<1||budget>2000000000ULL)
            throw std::runtime_error("Use --mode sv|za and --budget between 1 and 2000000000");
        auto rows=loadAll(repo);
        Search search(rows,mode,budget);
        std::vector<std::pair<string,U64>> phases;
        if(mode=="sv")svSearch(search,rows,phases);
        else zaSearch(search,rows,phases);
        search.report(out,phases);
        return 0;
    } catch(const std::exception& ex) {
        std::cerr<<"ERROR "<<ex.what()<<"\n";return 2;
    }
}
