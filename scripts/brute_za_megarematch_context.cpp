// Source-context constrained mega-rematch S-hash naming-grammar brute-force.
// Evidence: reconstructed ZAScripts Ev_sys_megarematch event and published
// PokeDocs original five missing ZA S hashes. H2 names only, not game strings.
// Compile: g++ -std=c++20 -O3 -DNDEBUG scripts/brute_za_megarematch_context.cpp -o brute_za_megarematch
// Run: ./brute_za_megarematch --out outputs/za-megarematch --budget 400000000
#include <algorithm>
#include <cctype>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using U64 = std::uint64_t;
using std::string;
using std::vector;
constexpr U64 BASIS=0xCBF29CE484222645ULL, PRIME=0x100000001B3ULL;
U64 extend(U64 x,const string& s) {for(unsigned char c:s)x=(x^c)*PRIME;return x;}
U64 digest(const string& s) {return extend(BASIS,s);}
string hex(U64 x) {char b[32];std::snprintf(b,sizeof b,"0x%016llX",(unsigned long long)x);return b;}

struct Target {U64 digest;int source_line;string observed_role;bool previously_H2;};
struct Hit {U64 digest;string candidate,kind,original_source;int line;bool previous;};
const vector<Target> targets={
  {0x062729EC443620C2ULL,23,"name_from_selection",true},
  {0x1463948047021356ULL,72,"selection_from_context_menu",true},
  {0x34AD86B7E5BB1526ULL,164,"boss_id_from_selection",false},
  {0x81E0610BF8B9337CULL,403,"megarematch_select_message_array",false},
  {0xD0F61B3481E43C08ULL,685,"megarematch_spn_boss_array",false},
};

int main(int argc,char** argv) {
  try {
    string out="za-megarematch";
    std::uint64_t budget=400000000,attempts=0;
    for(int i=1;i<argc;i++){
      string arg=argv[i];
      if(arg=="--out"&&i+1<argc)out=argv[++i];
      else if(arg=="--budget"&&i+1<argc)budget=std::stoull(argv[++i]);
      else throw std::runtime_error("Usage: --out path --budget 1..500000000");
    }
    if(budget<1||budget>500000000ULL)throw std::runtime_error("Budget outside 1..500M");
    // Independent known-vector controls drawn from preceding H2 research.
    if(digest("Get_BossName")!=targets[0].digest ||
       digest("Get_BossNameIndex")!=targets[1].digest)
      throw std::runtime_error("FNV64 known vectors disagree");

    const vector<string> words={
      "Boss","Name","Index","Spn","Species","Pokemon","Poke","Mon",
      "Param","Message","Msg","Select","Selection","Menu","Context","Text",
      "Word","Record","Time","Battle","Mega","Rematch","MegaRematch",
      "Megarematch","Icon","Model","Data","Array","List","Table","Id",
      "ID","No","Num","Count","Value","Type","Info","Event","Object",
      "State","Win","Lose","Result","Card","Reward","NameIndex","BossName",
      "BossSpn","BossPokemon","BossSpecies","BossIndex","BossNameIndex",
      "String","Label","Key","Numbers","Mons","DataList","IdList",
      "NameList","NameTable","BossList","Enemy","Target","Pkm","Pkmn",
      "Random","Party","UI","SelectMessage","SelectMsg","SpeciesName",
      "BossMon","RecordTime","MessageId","MsgId","Trainer","BattleId",
      "Pokedex","ListData","NoList"
    };
    const vector<string> prefixes={
      "","Get","Get_","get","get_","Set","Set_","Is","Is_",
      "Create","Create_","Check","Check_","GetBoss","Get_Boss",
      "Select","Select_","Find","Find_","Make","Make_","GetData",
      "Get_Data","Boss","Boss_","s_","m_","g_","_","getBoss"
    };
    const vector<string> suffixes={
      "","s","List","Table","Array","Data","Info","Index","Name",
      "ID","Id","Text","String","Str","No","Num","Count","Values",
      "Names","Param","Dic","Set","Records","_List","_Array","_Table","_Data"
    };
    std::unordered_map<U64,Target> matched;
    for(const auto& t:targets)matched.emplace(t.digest,t);
    vector<std::pair<string,U64>> pfx;
    for(const auto& p:prefixes)pfx.push_back({p,digest(p)});
    std::unordered_set<string> seen;
    vector<Hit> found;
    bool exhausted=false;
    auto trial=[&](const vector<string>& w,const string& phase)->bool{
      string camel,snake,upper,lc;
      for(size_t i=0;i<w.size();++i){
        camel+=w[i];
        if(i){snake+="_";upper+="_";}
        string token=w[i];
        if(!token.empty()&&token[0]>='A'&&token[0]<='Z')token[0]+=32;
        snake+=token;
        token=w[i];
        std::transform(token.begin(),token.end(),token.begin(),
          [](unsigned char c){return std::toupper(c);});
        upper+=token;
      }
      lc=camel;
      if(!lc.empty()&&lc[0]>='A'&&lc[0]<='Z')lc[0]+=32;
      for(const auto& stem:vector<string>{camel,snake,upper,lc}){
        for(const auto& [pre,pre_hash]:pfx){
          const U64 head=extend(pre_hash,stem);
          for(const auto& suffix:suffixes) {
            if(attempts>=budget){exhausted=true;return false;}
            ++attempts;
            const U64 value=extend(head,suffix);
            auto it=matched.find(value);
            if(it==matched.end())continue;
            const string candidate=pre+stem+suffix;
            if(digest(candidate)!=value)
              throw std::runtime_error("Incremental hash mismatch");
            if(!seen.insert(candidate).second)continue;
            const auto& t=it->second;
            found.push_back({value,candidate,phase,t.observed_role,t.source_line,t.previously_H2});
          }
        }
      }
      return true;
    };

    for(size_t a=0;a<words.size();++a)
      if(!trial({words[a]},"single_context_word"))goto done;
    for(size_t a=0;a<words.size();++a)
      for(size_t b=0;b<words.size();++b)
        if(!trial({words[a],words[b]},"pair_context_words"))goto done;
    for(size_t a=0;a<45;++a)
      for(size_t b=0;b<45;++b)
        for(size_t c=0;c<45;++c)
          if(!trial({words[a],words[b],words[c]},"triple_context_words"))goto done;
    done:
    std::sort(found.begin(),found.end(),[](const Hit& a,const Hit& b){
      return a.digest<b.digest||(a.digest==b.digest&&a.candidate<b.candidate);
    });
    std::ofstream tsv(out+"-matches.tsv");
    tsv<<"game\tkind\thash\tline\tcandidate\tevidence\tprior_H2_seed\tevent_role\n";
    for(const auto& hit:found)tsv<<"ZA\tS\t"<<hex(hit.digest)<<'\t'<<hit.line<<'\t'
      <<hit.candidate<<'\t'<<hit.kind<<'\t'<<(hit.previous?"YES":"NO")<<'\t'
      <<hit.original_source<<'\n';
    std::unordered_set<U64> distinct;
    int newly=0;
    for(const auto& hit:found)if(distinct.insert(hit.digest).second&&!hit.previous)++newly;
    std::ofstream summary(out+"-summary.json");
    summary<<"{\n \"game\":\"ZA\",\n \"version\":\"v2.0.2\",\n"
      <<" \"algorithm\":\"FNV-1a 64-bit source-constrained event word grammar\",\n"
      <<" \"input_scope\":\"Haxe reconstructed Ev_sys_megarematch context; not original native Lua source names\",\n"
      <<" \"expected_five_missing_S_hashes\":5,\n"
      <<" \"budget\":"<<budget<<",\n \"attempted_candidates\":"<<attempts
      <<",\n \"budget_exhausted\":"<<(exhausted?"true":"false")
      <<",\n \"matched_unique_target_hashes\":"<<distinct.size()
      <<",\n \"matched_hashes_not_in_prior_two_rounds\":"<<newly
      <<",\n \"native_original_name_confirmations\":0,\n \"hashlist_updates\":0\n}\n";
    std::cout<<"attempted="<<attempts<<" exhausted="<<exhausted
      <<" unique_matches="<<distinct.size()<<" new_targets="<<newly<<"\n";
    for(const auto& hit:found)std::cout<<hex(hit.digest)<<" "<<hit.candidate
      <<" [S:"<<hit.line<<"]\n";
    return 0;
  } catch(const std::exception& e) {
    std::cerr<<"ERROR "<<e.what()<<'\n';return 2;
  }
}
